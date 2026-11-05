"""Check the built site: python3 scripts/check_site.py http://127.0.0.1:8790/."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser()
parser.add_argument("base", nargs="?", default="http://127.0.0.1:8790/")
parser.add_argument("--screenshots", default=".blurt/site-check")
args = parser.parse_args()
shots = Path(args.screenshots)
shots.mkdir(parents=True, exist_ok=True)
errors = []
qiniu_requests = []


def is_qiniu_request(url):
    host = (urlparse(url).hostname or "").lower()
    return host == "img.pbtmcloud.cn" or any(
        host == suffix or host.endswith("." + suffix)
        for suffix in ["qiniu.com", "qiniu.io", "qbox.me", "clouddn.com", "qiniudn.com", "qiniucdn.com", "qnssl.com"])


def block_qiniu(route):
    qiniu_requests.append(route.request.url)
    route.abort()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
    context.route(lambda url: is_qiniu_request(url), block_qiniu)
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("response", lambda response: errors.append(f"HTTP {response.status}: {response.url}")
            if response.status >= 400 and response.url.startswith(args.base) else None)
    page.goto(args.base)
    data = page.evaluate("window.STUDIO_CONTENT")
    root = Path(__file__).resolve().parent.parent
    expected_skills = json.loads((root / "_data/studio_skills.json").read_text())
    expected_apps = json.loads((root / "_data/studio_apps.json").read_text())
    assert expected_skills and data["skills"] == expected_skills
    assert len({skill["id"] for skill in data["skills"]}) == len(data["skills"])
    assert data["apps"] == expected_apps
    assert len(data["photos"]) == 10
    assert len(data["posts"]) == 33
    for photo in data["photos"]:
        assert photo["src"].startswith("/assets/studio/photos/"), photo["src"]
    routes = ["home", "workflows", "skills", "apps", "blog", "knowledge", "photos",
              "flow/photography", "flow/presentation", "flow/writing", "flow/agent-work",
              "app/agent-notebook", "app/agent-note-cli"]
    routes += ["skill/" + skill["id"] for skill in data["skills"]]
    for width in [1440, 375]:
        page.set_viewport_size({"width": width, "height": 1000 if width == 1440 else 812})
        for route in routes:
            page.goto(args.base + "#" + route)
            expect(page.locator("main h1")).to_have_count(1)
            expect(page.locator('#navigation a[aria-current="page"]')).to_have_count(1)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (width, route)
        for route in ["home", "apps", "photos", "flow/agent-work"]:
            page.goto(args.base + "#" + route)
            page.evaluate("document.fonts.ready")
            if route == "photos":
                page.locator(".photo-gallery img").evaluate_all("imgs => imgs.forEach(img => img.loading='eager')")
                page.wait_for_function("[...document.querySelectorAll('.photo-gallery img')].every(img=>img.complete&&img.naturalWidth>0)")
                sizes = page.locator(".photo-gallery img").evaluate_all("imgs=>imgs.map(img=>[img.naturalWidth,img.naturalHeight])")
                assert len(sizes) == 10 and all(0 < max(size) <= 1920 for size in sizes), sizes
                assert page.locator(".photo-caption, figcaption").count() == 0
                boxes = page.locator(".photo-item").evaluate_all("items=>items.map(item=>({box:item.getBoundingClientRect().toJSON(),ratio:Number(item.querySelector('img').width)/Number(item.querySelector('img').height)}))")
                for item in boxes:
                    assert abs(item["box"]["width"]/item["box"]["height"]-item["ratio"]) < 0.02
            page.screenshot(path=str(shots / f"{width}-{route.replace('/', '-')}.png"), full_page=True, animations="disabled")
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(args.base + "#skills")
    page.get_by_role("button", name="图像与多模态", exact=True).click()
    expected_multimodal = sum(skill["category"] == "图像与多模态" for skill in data["skills"])
    expect(page.locator(".skill-card:visible")).to_have_count(expected_multimodal)
    page.get_by_role("button", name="全部", exact=True).click()
    page.get_by_role("searchbox").fill("摄影师")
    expect(page.locator(".skill-card:visible")).to_have_count(1)
    page.get_by_role("searchbox").fill("no-match-test")
    expect(page.locator(".empty")).to_be_visible()
    page.goto(args.base + "#apps")
    page.get_by_role("tab", name="命令行", exact=True).click()
    cli = next(app for app in expected_apps if app["id"] == "agent-note-cli")
    expect(page.locator(".install-command")).to_contain_text(cli["installCommand"])
    expect(page.locator("#app-panel")).to_contain_text(cli["version"])
    expect(page.locator("#app-panel")).to_have_attribute("aria-labelledby", "tab-agent-note-cli")
    page.keyboard.press("ArrowLeft")
    expect(page.get_by_role("tab", name="桌面端", exact=True)).to_be_focused()
    expect(page.locator("#app-panel .product-screenshot")).to_have_attribute("src", "/assets/studio/agent-notebook-preview.png")
    unsafe_text = '<img src=x onerror="window.__maintenanceXss=true">'
    page.evaluate("value=>Object.assign(window.STUDIO_CONTENT.apps[0],{headline:value,description:value,version:value})", unsafe_text)
    page.goto(args.base + "#app/agent-notebook")
    expect(page.locator(".app-panel-copy h3")).to_have_text(unsafe_text)
    expect(page.locator(".app-description")).to_have_text(unsafe_text)
    assert page.locator(".app-panel-copy img").count() == 0
    assert page.evaluate("window.__maintenanceXss !== true")
    page.evaluate("apps=>window.STUDIO_CONTENT.apps.forEach((app,index)=>Object.assign(app,apps[index]))", expected_apps)
    page.goto(args.base + "#flow/agent-work")
    page.locator('.related a[href="/#skill/project-handoff"]').click()
    expect(page.locator("main h1")).to_have_text("项目交接")
    page.goto(args.base + "#knowledge")
    page.get_by_role("button", name="视觉表达", exact=True).click()
    expect(page.locator(".node-description h2")).to_have_text("视觉表达")
    page.get_by_role("link", name="进入 PPT 工作流", exact=True).click()
    expect(page.locator("main h1")).to_have_text("把研究，讲成一份好 PPT")
    page.goto(args.base + "#photos")
    opener = page.locator("[data-photo='0']")
    opener.click()
    expect(page.get_by_role("dialog")).to_be_visible()
    page.get_by_role("button", name="下一张", exact=True).click()
    expect(page.locator("#dialog-title")).to_have_text("摄影作品 2 / 10")
    page.keyboard.press("ArrowLeft")
    expect(page.locator("#dialog-title")).to_have_text("摄影作品 1 / 10")
    page.keyboard.press("Escape")
    expect(page.get_by_role("dialog")).not_to_be_visible()
    expect(opener).to_be_focused()
    page.set_viewport_size({"width": 375, "height": 812})
    page.goto(args.base + "#home")
    page.get_by_role("button", name="展开导航", exact=True).click()
    page.locator("#navigation").get_by_role("link", name="摄影", exact=True).click()
    expect(page.locator("main h1")).to_have_text("摄影")
    expect(page.locator(".menu-toggle")).to_have_attribute("aria-expanded", "false")
    page.get_by_role("link", name="跳到正文", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.locator("main")).to_be_focused()
    for post in data["posts"]:
        response = page.goto(args.base.rstrip("/") + post["url"], wait_until="domcontentloaded")
        assert response.status == 200, post["url"]
        expect(page.locator(".post-heading h1")).to_have_text(post["title"])
        expect(page.locator(".post-body")).not_to_be_empty()
        assert page.locator("main").get_attribute("data-document") == "post"
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), post["url"]
        local_images = page.locator(".post-body img").evaluate_all("imgs=>imgs.map(img=>img.getAttribute('src')).filter(src=>src&&src.startsWith('/'))")
        for image_url in local_images:
            image_response = context.request.get(args.base.rstrip("/") + image_url)
            assert image_response.ok, image_url
        page.evaluate("document.querySelectorAll('.post-body img').forEach(img=>img.loading='lazy')")
    for path in ["tags/", "about/", "404.html", "feed.xml"]:
        response = context.request.get(args.base + path)
        assert response.ok, path
    math_post = next(post for post in data["posts"] if "GAN完整理论推导" in post["title"])
    page.goto(args.base.rstrip("/") + math_post["url"], wait_until="domcontentloaded")
    page.wait_for_selector("mjx-container")
    page.evaluate("window.MathJax.startup.promise")
    assert page.locator("mjx-container").count() > 0
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "rendered math must stay inside the mobile viewport"
    page.route("https://wdblink.disqus.com/embed.js", lambda route: route.fulfill(body="", content_type="text/javascript"))
    page.locator(".post-comments summary").click()
    page.wait_for_function("typeof window.disqus_config==='function'")
    discussion = page.evaluate("(()=>{const config={page:{}};window.disqus_config.call(config);return config.page;})()")
    assert discussion["identifier"] == page.locator(".post-comments").get_attribute("data-discussion-id")
    assert discussion["url"].startswith("https://wdblink.github.io/2019/01/21/")
    assert not qiniu_requests, qiniu_requests
    assert not errors, errors
    browser.close()

print(f"PASS: {len(routes)} routes at 1440/375px; 33 real posts; filters, links, app tabs, photo dialog, mobile nav and local assets.")
print("PASS: 10 compressed gallery images loaded from this site; zero Qiniu resource requests.")
