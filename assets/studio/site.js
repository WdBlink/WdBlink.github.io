const {skills, photos, posts} = window.STUDIO_CONTENT;
const main = document.querySelector('main');
const navigation = document.querySelector('#navigation');
const dialog = document.querySelector('#dialog');
const asset = name => '/assets/studio/' + name;
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const byId = (items, id) => items.find(item => item.id === id);
const routeUrl = route => '/#' + route;
const link = (url, label, className='') => '<a class="' + className + '" href="' + escapeHtml(url) + '">' + escapeHtml(label) + '</a>';
const tags = items => '<div class="pills metadata">' + items.map(item => '<span class="pill neutral">' + escapeHtml(item) + '</span>').join('') + '</div>';
const intro = (title, description, subtitle='') => '<div class="page-intro">' + (subtitle ? '<p class="subtitle">' + escapeHtml(subtitle) + '</p>' : '') + '<h1>' + escapeHtml(title) + '</h1><p>' + escapeHtml(description) + '</p></div>';
const back = (route, label) => link(routeUrl(route), '返回' + label, 'back');

const apps = [
  {id:'agent-notebook', title:'Agent Notebook', label:'桌面端', repository:'https://github.com/WdBlink/agent-notebook', action:'下载 macOS 版', url:'https://github.com/WdBlink/agent-notebook/releases/latest'},
  {id:'agent-note-cli', title:'agent-note-cli', label:'命令行', repository:'https://github.com/WdBlink/agent-note-cli', action:'查看安装与使用', url:'https://github.com/WdBlink/agent-note-cli#readme'},
];

const workflows = [
  {id:'photography', title:'从一次拍摄，到一组作品', category:'摄影', description:'观察、拍摄、选片、编排。把按下快门之后的事，也认真做完。', thumb:'photo', skillIds:['photographer-style','social-cover-maker'], appIds:[], result:'photos',
    sections:[
      ['先理解自己想看见什么','带着相机出门之前，可以先研究一位摄影师：他如何处理光线、色彩与画面里的关系？摄影师风格拆解 Skill 把参考作品与分析放在一起。借用的是观看问题的方式，不是给每张照片套上相同滤镜。'],
      ['把选择留给摄影师','拍摄时先留意真实的现场。回到照片前，再比较相似画面，留下关系更清楚、情绪更准确的那一张。技术分析能提供线索，但不能代替对画面的判断。'],
      ['先把照片排成一组，再考虑发布','把候选作品放在一起，检查开场、重复与收尾。作品页尽量让照片自己说话；需要为一篇摄影文章做封面时，再调用社交平台封面 Skill。封面服务于发布，不改变照片本身。'],
      ['让下一次观看带来修订','用完整画幅检查裁切与影调，再分别看桌面和手机上的顺序。本站摄影页展示的是选定的实拍作品，不为它们额外编造名字或故事。']
    ]},
  {id:'presentation', title:'把研究，讲成一份好 PPT', category:'办公', description:'从资料中找到问题，从问题中提炼观点，最后才是页面。', thumb:'ppt', skillIds:['paper-deconstruction','academic-writing-storytelling','pv-forecast-pptx'], appIds:[], result:'skills',
    sections:[
      ['让资料回答一个具体问题','先写下听众需要理解的判断。阅读论文时，用论文精读 Skill 拆开结构、方法和证据，保留原文出处。不要因为一张图好看，就把它放进演示。'],
      ['把论证组织成可以讲述的顺序','学术写作讲故事框架能辅助检查问题、转折与证据之间的关系。叙事帮助听众理解，不负责掩盖反例、边界或尚未验证的结论。'],
      ['选对任务范围，再调用模板','光伏预测汇报 PPTX Skill 面向光伏与能源预测研究，有自己的模板和资源。适合这类专题时再使用；它不是覆盖所有主题的通用 PPT 生成器。'],
      ['用一次真实试讲检查结果','按演讲时长讲一遍。逐页核对数据、坐标、来源和结论，把解释不清的页面退回到材料与结构，而不是继续添加装饰。']
    ]},
  {id:'writing', title:'让想法成为值得读的文章', category:'写作', description:'从一个真实问题开始，留下来源，经过起草与编辑，形成自己的表达。', thumb:'writing', skillIds:['transcript-source-compiler','human-understanding'], appIds:['agent-notebook'], result:'blog',
    sections:[
      ['先留下材料，不急着写结论','工作中的判断、一次对话或一段分享，都可能是文章的起点。Agent Notebook 可以帮助回看 Agent 工作的会话与证据；这些私人记录不需要为了写作而全部公开。'],
      ['把转写稿变成可靠的来源','面对大段口述材料，转写来源编译器先区分原话、事实与解释，再整理成可追溯的底稿。口述时的重复可以合并，证据不足的地方则应该保留边界。'],
      ['写清楚谁做了什么','结果理解与证据解释 Skill 帮助固定术语、拆开条件和结果，必要时补一个读者能跟下来的例子。图解是为了理解某个关系，不是文章必须配齐的装饰。'],
      ['回到原文，完成最后一次核对','编辑时检查每个观点由什么支持，删掉重复与空话，保留自己的语气。旧博客里的文章保留原日期和内容，继续作为这些思考的记录。']
    ]},
  {id:'agent-work', title:'让 Agent 工作，明天还能继续', category:'AI 工作流', description:'从会话记录到工作线，再到人工收束与项目交接。', thumb:'notebook', skillIds:['project-handoff','mind-map'], appIds:['agent-notebook','agent-note-cli'], result:'apps',
    sections:[
      ['先回看发生了什么','桌面端适合浏览 Today 工作现场，命令行端适合在终端进入同一产品体系。先看原始会话与来源，再决定哪些变化值得整理，避免把一次生成的总结直接当成事实。'],
      ['把会话整理成可以继续的工作线','围绕具体问题串起进展、当前停点与证据。Agent Notebook 的 Today 保留 raw、compiled、stale 与 sealed 状态，区分原始记录、整理结果、待更新内容与人工封页。'],
      ['让人完成收束，而不是只确认一段摘要','检查遗漏、分歧与下一步。项目思维导图 Skill 可以把明确的判断组织成节点；项目交接 Skill 则核对项目资产与历史，生成能独立阅读的交接材料。'],
      ['保留工作上下文，也保留隐私边界','公开网站只介绍方法与工具。真实会话、私人笔记和未公开证据仍留在本地。能继续工作，比把所有记录展示出来更重要。']
    ]},
];

const domains = [
  {id:'ai',title:'人工智能',x:26,y:23,description:'理解模型的能力与边界，把 AI 放进具体工作。',link:'flow/agent-work',label:'进入 Agent 工作流'},
  {id:'research',title:'研究方法',x:68,y:18,description:'围绕问题收集证据，比较解释，区分事实与推断。',link:'skill/paper-deconstruction',label:'查看论文精读 Skill'},
  {id:'tools',title:'软件创造',x:50,y:49,description:'用小工具解决真实工作中的摩擦，让方法成为可用的产品。',link:'apps',label:'看看工具与应用'},
  {id:'business',title:'商业思考',x:18,y:64,description:'理解需求、价值与约束，检验不确定条件下的判断。',link:'skill/thinking-in-bets',label:'查看对赌决策工作流'},
  {id:'visual',title:'视觉表达',x:78,y:61,description:'研究图像、叙事与信息结构，让复杂内容更容易理解。',link:'flow/presentation',label:'进入 PPT 工作流'},
  {id:'life',title:'生活与观察',x:48,y:82,description:'在摄影、阅读和日常经验中积累，用真实的观察校正想法。',link:'photos',label:'看看摄影选集'},
];

const pages = {
  home:['首页',homePage], workflows:['Workflows',workflowsPage], skills:['Skills',skillsPage],
  apps:['Apps',appsPage], blog:['Blog',blogPage], knowledge:['知识地图',knowledgePage], photos:['摄影',photosPage],
};
const detailPages = {
  flow:{parent:'workflows',render:flowPage}, skill:{parent:'skills',render:skillPage}, app:{parent:'apps',render:appPage},
};
let activePhoto = 0;
let photoOpener = null;

function thumbnail(kind) {
  const thumbs = {
    photo:'<div class="thumb"><img src="' + photos[0].src + '" alt="" loading="lazy" width="1920" height="1280"></div>',
    ppt:'<div class="thumb thumb-ppt" aria-hidden="true"><div class="mini-slide"><strong>先有观点，</strong><strong>再有页面。</strong><i></i><span>叙事 / 证据</span></div></div>',
    writing:'<div class="thumb thumb-writing" aria-hidden="true"><div class="mini-note">一个好问题<span></span>一些新线索<span></span>自己的表达</div></div>',
    notebook:'<div class="thumb thumb-notebook"><img src="' + asset('agent-notebook-icon.png') + '" alt="" loading="lazy" width="96" height="96"></div>',
  };
  return thumbs[kind];
}

function workflowRow(flow) {
  return '<a class="resource-row" href="' + routeUrl('flow/' + flow.id) + '">' + thumbnail(flow.thumb) + '<div><h3>' + flow.title + '</h3><p>' + flow.description + '</p>' + tags([flow.category, flow.appIds.length ? 'Skills 与 Apps' : 'Skills']) + '</div></a>';
}

function homePage() {
  return '<section aria-label="自我介绍"><div class="name-line"><h1>尹鹏宇</h1><svg viewBox="0 0 80 30" aria-hidden="true"><path d="M2 24Q37 2 73 12M65 7l8 5-8 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg><span class="name-en">WdBlink</span></div><div class="intro-copy"><p>你好，欢迎来到我的一小块互联网。</p><p>我喜欢研究 <span class="wavy">AI 如何改变个人的工作方式</span>，也喜欢摄影、写作，以及动手做一些解决实际问题的小工具。</p><p>这里整理着我的工作流、可复用的 Skills、创造的 Apps，和一路积累的文字与影像。<span class="inline-highlight">把学到的东西，变成做出来的东西。</span></p></div><p class="hand-note hello-note">你可以从下面这些工作方式，开始认识我。</p></section>' +
    '<section><div class="section-heading"><h2><span class="marker">我是如何工作的</span></h2>' + link(routeUrl('workflows'),'全部工作流') + '</div><div class="resource-list">' + workflows.slice(0,3).map(workflowRow).join('') + '</div></section>' +
    '<div class="home-bottom"><section><div class="section-heading"><h2><span class="marker green">做一点东西</span></h2>' + link(routeUrl('apps'),'所有 Apps') + '</div><a class="mini-entry" href="' + routeUrl('app/agent-notebook') + '"><img class="home-app-icon" src="' + asset('agent-notebook-icon.png') + '" alt="" width="56" height="56"><h3>Agent Notebook</h3><p>回看 Agent 工作，整理线索，继续下一步。</p>' + tags(['桌面端','命令行']) + '</a></section><section><div class="section-heading"><h2><span class="marker lavender">一些思考</span></h2>' + link(routeUrl('blog'),'文章归档') + '</div>' + posts.slice(0,2).map(post => '<a class="mini-entry" href="' + escapeHtml(post.url) + '"><h3>' + escapeHtml(post.title) + '</h3><p>' + escapeHtml(post.excerpt) + '</p><time>' + post.date + '</time></a>').join('') + '</section></div>';
}

function workflowsPage() {
  return intro('Workflows','做事的方法，比工具清单更有意思。把一次实践展开，看看不同能力和工具如何配合。') + '<div class="resource-list flow-list">' + workflows.map(workflowRow).join('') + '</div><p class="flow-quote">工具在变，自己的判断始终在场。</p>';
}

function flowPage(id) {
  const flow = byId(workflows,id);
  if (!flow) return notFound();
  return back('workflows','工作流') + intro(flow.title,flow.description,flow.category + '工作流') + '<div class="detail-grid"><article class="workflow-reading">' + flow.sections.map(([title,text]) => '<section><h2>' + title + '</h2><p>' + text + '</p></section>').join('') + '</article><aside class="related"><h2>用到的能力与工具</h2>' + flow.skillIds.map(id => link(routeUrl('skill/' + id),byId(skills,id).title)).join('') + flow.appIds.map(id => link(routeUrl('app/' + id),byId(apps,id).title)).join('') + link(routeUrl(flow.result),'看看' + pages[flow.result][0]) + '</aside></div>';
}

function filterBar(categories, placeholder) {
  return '<div class="catalog-controls"><div class="filters" role="group" aria-label="分类筛选">' + ['全部',...categories].map((category,index) => '<button data-filter="' + escapeHtml(category) + '" aria-pressed="' + (index===0) + '">' + escapeHtml(category) + '</button>').join('') + '</div><label class="search"><span hidden>搜索' + placeholder + '</span><input type="search" placeholder="搜索' + placeholder + '" aria-label="搜索' + placeholder + '"></label></div><p class="result-status" role="status" aria-live="polite"></p>';
}

function skillsPage() {
  return intro('Skills','把经验整理成可重复使用的能力。按场景寻找方法，了解它能解决什么，再带进自己的工作流。') + filterBar([...new Set(skills.map(skill => skill.category))],'技能') + '<div class="skill-grid">' + skills.map(skill => '<a class="skill-card filter-item" data-category="' + skill.category + '" href="' + routeUrl('skill/' + skill.id) + '"><div class="skill-meta"><span>' + skill.category + '</span><span>' + (skill.license==='MIT'?'MIT 开源':'保留许可') + '</span></div><h2>' + escapeHtml(skill.title) + '</h2><p>' + escapeHtml(skill.description) + '</p>' + tags([skill.name]) + '</a>').join('') + '</div><p class="empty" hidden>没有找到匹配的技能，试试其他关键词。</p><p class="tools-note">目录来自 LLM-Skills。许可说明不代表价格；使用范围以各 Skill 的 LICENSE 与文档为准。</p>';
}

function skillPage(id) {
  const skill = byId(skills,id);
  if (!skill) return notFound();
  const usedIn = workflows.filter(flow => flow.skillIds.includes(id));
  return back('skills','Skills') + intro(skill.title,skill.description,skill.name) + '<div class="detail-grid"><article class="skill-body"><h2>使用这项能力</h2><p>从真实任务出发，先阅读 Skill 的输入要求、适用范围与所需工具，再按说明在自己的 Agent 环境中使用。</p>' + (skill.source ? '<div class="button-group">' + link(skill.source,'查看 Skill 与使用说明','button') + '</div>' : '<p class="tools-note">当前已收录能力介绍，指令尚未在公开仓库发布。</p>') + '<h2>版本与许可</h2><p>目录版本 ' + escapeHtml(skill.version) + '。' + (skill.license==='MIT'?'MIT 开源许可，具体条件请阅读源仓库的许可文件。':'采用保留许可，请以该 Skill 文档中的授权范围为准。') + '</p>' + link('https://github.com/WdBlink/LLM-Skills','查看 LLM-Skills 仓库','quiet-link') + '</article><aside class="related"><h2>放进一条工作流</h2>' + (usedIn.length ? usedIn.map(flow => link(routeUrl('flow/' + flow.id),flow.title)).join('') : link(routeUrl('workflows'),'浏览所有工作流')) + '</aside></div>';
}

function appPanel(id) {
  const app = byId(apps,id);
  const desktop = id==='agent-notebook';
  return '<div class="app-panel-copy"><h3>' + (desktop?'把 Agent 的工作，整理成可继续的线索。':'在终端里，继续同一份工作。') + '</h3><p class="app-description">' + (desktop?'本地优先的 macOS 应用。回看 Codex 与 Claude Code 的会话，把工作现场整理成带来源的工作线，并由人完成收束。':'Agent Notebook 的命令行入口。浏览会话与工作线，使用只读终端界面回看进展，也可进入结构化 Today 工作流。') + '</p><div class="button-group">' + link(app.url,app.action,'button') + link(app.repository,'GitHub 源码','button secondary') + '</div></div>' +
    (desktop?'<img class="product-screenshot" src="' + asset('agent-notebook-preview.png') + '" alt="Agent Notebook 桌面端 Today 界面，展示示例会话、工作时间线与来源筛选" width="1440" height="1000" fetchpriority="high">':'<div class="install-command"><code>brew install wdblink/tap/agent-note-cli</code><button data-copy="brew install wdblink/tap/agent-note-cli">复制命令</button></div><picture><source media="(prefers-reduced-motion: reduce)" srcset="' + asset('agent-note-poster.png') + '"><img class="product-screenshot cli-screenshot" src="' + asset('agent-note-preview.gif') + '" alt="agent-note-cli 终端演示，使用合成会话与固定示例数据展示工作线和证据阅读" width="1090" height="630" fetchpriority="high"></picture>') +
    '<p class="app-caption">' + (desktop?'公开界面截图，内容为示例工作记录。':'终端演示使用合成会话与固定示例数据，不含私人记录。') + '</p>';
}

function appFeature(active='agent-notebook') {
  return '<section class="app-feature"><div class="app-heading"><div class="product-brand"><img src="' + asset('agent-notebook-icon.png') + '" alt="" width="64" height="64"><div><h2>Agent Notebook</h2><p>同一个产品，两种工作入口。</p></div></div>' + tags(['MIT 开源','本地优先']) + '</div><div class="app-tabs" role="tablist" aria-label="产品形态">' + apps.map(app => '<button role="tab" id="tab-' + app.id + '" aria-controls="app-panel" aria-selected="' + (app.id===active) + '" data-app-view="' + app.id + '">' + app.label + '</button>').join('') + '</div><div id="app-panel" role="tabpanel" aria-labelledby="tab-' + active + '">' + appPanel(active) + '</div></section>';
}

function appsPage() {
  return intro('Apps','从具体的问题出发，做一些顺手的工具。这里是已经可以使用的产品。') + appFeature() + '<div class="app-benefits"><section><h2>回看工作</h2><p>从会话与来源开始，知道进展从哪里来。</p></section><section><h2>整理线索</h2><p>把记录组织成工作线，保留当前停点与证据。</p></section><section><h2>继续推进</h2><p>人工收束，再把上下文交给下一步。</p></section></div>' + link(routeUrl('flow/agent-work'),'看看它们如何进入工作流','quiet-link');
}

function appPage(id) {
  if (!byId(apps,id)) return notFound();
  return back('apps','Apps') + intro('Agent Notebook','桌面端与命令行，是同一个产品体系的两种入口。') + appFeature(id) + '<div class="related app-related"><h2>相关工作流</h2>' + workflows.filter(flow => flow.appIds.includes(id)).map(flow => link(routeUrl('flow/' + flow.id),flow.title)).join('') + '</div>';
}

function articleCategory(post) {
  const text = post.title + ' ' + post.tags.join(' ');
  if (/学习|GAN|NNI|uncertainty|Brats|检测|分割|AI|神经网络/i.test(text)) return 'AI 与研究';
  if (/感想|灵感|Key Result|球鞋|博客搭建|毕业/.test(text)) return '生活与观察';
  return '技术笔记';
}

function blogPage() {
  return intro('Blog','保留写下这些文章时的问题与思考，也保留一路走来的痕迹。') + filterBar(['AI 与研究','技术笔记','生活与观察'],'文章') + '<div>' + posts.map(post => '<a class="article-row filter-item" data-category="' + articleCategory(post) + '" href="' + escapeHtml(post.url) + '"><time class="article-category">' + post.date + '</time><div><h2>' + escapeHtml(post.title) + '</h2><p>' + escapeHtml(post.excerpt) + '</p>' + tags(post.tags.slice(0,3)) + '</div></a>').join('') + '</div><p class="empty" hidden>暂时没有匹配的文章，换个关键词试试。</p>';
}

function knowledgePage() {
  return intro('知识地图','一些持续探索的领域，以及它们之间的联系。这里分享知识的轮廓，私人笔记留在自己的空间。') + '<div class="map-panel" role="group" aria-label="知识领域关联图"><svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><path d="M26 23L68 18L50 49L18 64L26 23M50 49L78 61L68 18M78 61L48 82L18 64M26 23L50 49L48 82" fill="none" stroke="currentColor" stroke-width=".18" stroke-dasharray="1 1"/></svg>' + domains.map((domain,index) => '<button class="map-node" style="left:' + domain.x + '%;top:' + domain.y + '%" data-domain="' + domain.id + '" aria-pressed="' + (index===0) + '">' + domain.title + '</button>').join('') + '<span class="map-caption">点击一个主题，顺着线索继续。</span></div><div class="node-description" aria-live="polite"></div><p class="tools-note">只展示公开领域与本站入口，不载入私人笔记。</p>';
}

function describeDomain(id) {
  const domain = byId(domains,id);
  main.querySelector('.node-description').innerHTML = '<h2>' + domain.title + '</h2><div><p>' + domain.description + '</p>' + link(routeUrl(domain.link),domain.label) + '</div>';
  main.querySelectorAll('[data-domain]').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.domain===id)));
}

function photosPage() {
  return '<div class="photo-intro">' + intro('摄影','') + '<blockquote><p>“摄影是一种语言。”</p><cite><a href="https://articles.anseladams.com/ansel-adams-quotes/">Ansel Adams</a></cite></blockquote></div><div class="photo-gallery" aria-label="摄影作品选集"></div>';
}

function layoutPhotos() {
  const gallery = main.querySelector('.photo-gallery');
  if (!gallery) return;
  const width = gallery.clientWidth;
  const remaining = photos.map((photo,index) => ({...photo,index,ratio:photo.width/photo.height}));
  const rows = [];
  while (remaining.length) {
    let count = 1;
    if (width > 560) {
      let closest = Infinity;
      for (let n=2;n<=Math.min(4,remaining.length);n++) {
        if (remaining.length-n===1) continue;
        const sum = remaining.slice(0,n).reduce((total,photo) => total+photo.ratio,0);
        const distance = Math.abs((width-(n-1)*18)/sum-245);
        if (distance < closest) {closest=distance;count=n;}
      }
    }
    rows.push(remaining.splice(0,count));
  }
  gallery.innerHTML = rows.map(row => '<div class="photo-row">' + row.map(photo => '<figure style="flex:' + photo.ratio + '"><button class="photo-item" data-photo="' + photo.index + '" aria-label="放大查看：' + escapeHtml(photo.alt) + '" style="aspect-ratio:' + photo.width + '/' + photo.height + '"><img src="' + photo.src + '" alt="' + escapeHtml(photo.alt) + '" width="' + photo.width + '" height="' + photo.height + '" ' + (photo.index>2?'loading="lazy"':photo.index===0?'fetchpriority="high"':'') + '></button></figure>').join('') + '</div>').join('');
}

function notFound() {
  return intro('这一页还没有写好。','可以先去其他地方走走。') + link(routeUrl('home'),'返回首页','button');
}

function setNavigation(parent) {
  navigation.innerHTML = Object.entries(pages).map(([name,[title]]) => '<a href="' + routeUrl(name) + '" ' + (name===parent?'aria-current="page"':'') + '>' + title + '</a>').join('');
  navigation.classList.remove('open');
  document.querySelector('.menu-toggle').setAttribute('aria-expanded','false');
  document.querySelector('.menu-toggle').setAttribute('aria-label','展开导航');
}

function render() {
  if (main.dataset.document) {setNavigation(main.dataset.document==='page'?'home':'blog');return;}
  const [route,id] = location.hash.replace(/^#\/?/,'').split('/');
  const key = route || 'home';
  const page = pages[key];
  const detail = detailPages[key];
  const parent = page?key:detail?.parent;
  if (dialog.open) dialog.close();
  main.innerHTML = page?page[1]():detail?detail.render(id):notFound();
  setNavigation(parent);
  const detailTitle = key==='flow'?byId(workflows,id)?.title:key==='skill'?byId(skills,id)?.title:key==='app'?byId(apps,id)?.title:null;
  document.title = (detailTitle || pages[parent]?.[0] || '页面') + ' / 尹鹏宇 WdBlink';
  if (key==='knowledge') describeDomain('ai');
  if (key==='photos') layoutPhotos();
  window.scrollTo(0,0);
}

function filterItems() {
  const category = main.querySelector('[data-filter][aria-pressed=true]')?.dataset.filter || '全部';
  const query = (main.querySelector('input[type=search]')?.value || '').trim().toLocaleLowerCase();
  let shown = 0;
  main.querySelectorAll('.filter-item').forEach(item => {
    item.hidden = (category!=='全部' && item.dataset.category!==category) || !item.textContent.toLocaleLowerCase().includes(query);
    if (!item.hidden) shown++;
  });
  main.querySelector('.empty').hidden = shown!==0;
  main.querySelector('.result-status').textContent = category==='全部' && !query?'':shown + ' 项结果';
}

function showPhoto(index) {
  activePhoto = (index+photos.length)%photos.length;
  const photo = photos[activePhoto];
  document.querySelector('#dialog-title').textContent = '摄影作品 ' + (activePhoto+1) + ' / ' + photos.length;
  document.querySelector('#dialog-body').innerHTML = '<img class="lightbox-img" src="' + photo.src + '" alt="' + escapeHtml(photo.alt) + '" width="' + photo.width + '" height="' + photo.height + '"><div class="lightbox-controls"><button data-photo-step="-1">上一张</button><span>尹鹏宇 WdBlink</span><button data-photo-step="1">下一张</button></div>';
  if (!dialog.open) dialog.showModal();
}

document.querySelector('.menu-toggle').addEventListener('click',event => {
  const button = event.currentTarget;
  const open = button.getAttribute('aria-expanded')!=='true';
  button.setAttribute('aria-expanded',String(open));
  button.setAttribute('aria-label',open?'收起导航':'展开导航');
  navigation.classList.toggle('open',open);
});
document.querySelector('.skip').addEventListener('click',event => {event.preventDefault();main.focus();});
document.addEventListener('click',async event => {
  const button = event.target.closest('button');
  if (!button) return;
  if (button.matches('.close')) dialog.close();
  if (button.dataset.filter) {main.querySelectorAll('[data-filter]').forEach(item => item.setAttribute('aria-pressed',String(item===button)));filterItems();}
  if (button.dataset.domain) describeDomain(button.dataset.domain);
  if (button.dataset.photo!==undefined) {photoOpener=button;showPhoto(Number(button.dataset.photo));}
  if (button.dataset.photoStep) {const step=Number(button.dataset.photoStep);showPhoto(activePhoto+step);dialog.querySelector('[data-photo-step="' + step + '"]').focus();}
  if (button.dataset.appView) {
    main.querySelectorAll('[data-app-view]').forEach(item => item.setAttribute('aria-selected',String(item===button)));
    const panel = main.querySelector('#app-panel');
    panel.innerHTML = appPanel(button.dataset.appView);
    panel.setAttribute('aria-labelledby',button.id);
  }
  if (button.dataset.copy) {
    try {await navigator.clipboard.writeText(button.dataset.copy);button.textContent='已复制';}
    catch {button.textContent='请选中命令复制';}
  }
});
dialog.addEventListener('close',() => {if (photoOpener?.isConnected) photoOpener.focus({preventScroll:true});});
document.addEventListener('keydown',event => {
  if (dialog.open && ['ArrowLeft','ArrowRight'].includes(event.key)) {event.preventDefault();showPhoto(activePhoto+(event.key==='ArrowRight'?1:-1));dialog.querySelector('.close').focus();}
  const current = event.target.closest('[role=tab]');
  if (current && ['ArrowLeft','ArrowRight'].includes(event.key)) {
    event.preventDefault();
    const tabs = [...main.querySelectorAll('[role=tab]')];
    const next = tabs[(tabs.indexOf(current)+(event.key==='ArrowRight'?1:tabs.length-1))%tabs.length];
    next.click();next.focus();
  }
});
main.addEventListener('input',event => {if (event.target.matches('input[type=search]')) filterItems();});
let resizeTimer;
window.addEventListener('resize',() => {clearTimeout(resizeTimer);resizeTimer=setTimeout(layoutPhotos,100);});
window.addEventListener('hashchange',() => {if (!main.dataset.document) {render();main.focus({preventScroll:true});}});
document.querySelector('.post-comments')?.addEventListener('toggle',event => {
  if (!event.currentTarget.open || document.querySelector('script[data-disqus]')) return;
  const section = event.currentTarget;
  window.disqus_config = function () {
    this.page.identifier = section.dataset.discussionId;
    this.page.url = section.dataset.discussionUrl;
  };
  const script = document.createElement('script');
  script.src = 'https://wdblink.disqus.com/embed.js';
  script.dataset.disqus = 'true';
  document.body.append(script);
});
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(registrations => Promise.all(registrations.filter(registration => registration.active?.scriptURL===location.origin+'/sw.js').map(registration => registration.unregister()))).catch(() => {});
}
render();
const mathSources = document.querySelectorAll('.post-body script[type^="math/tex"]');
if (document.querySelector('.post-body')?.textContent.includes('$') || mathSources.length) {
  mathSources.forEach(source => {
    const display = source.type.includes('mode=display');
    source.replaceWith(document.createTextNode((display?'\\[':'\\(') + source.textContent + (display?'\\]':'\\)')));
  });
  window.MathJax = {tex:{inlineMath:[['$','$'],['\\(','\\)']]},svg:{fontCache:'global'}};
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js';
  script.async = true;
  document.head.append(script);
}
