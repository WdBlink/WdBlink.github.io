---
layout: null
permalink: /assets/studio/content.js
---
window.STUDIO_CONTENT = {
  skills: {{ site.data.studio_skills | jsonify }},
  apps: {{ site.data.studio_apps | jsonify }},
  photos: {{ site.data.studio_photos | jsonify }},
  posts: [
  {% for post in site.posts %}
    {
      "title": {{ post.title | jsonify }},
      "url": {{ post.url | relative_url | jsonify }},
      "date": {{ post.date | date: "%Y-%m-%d" | jsonify }},
      "tags": {{ post.tags | jsonify }},
      "excerpt": {{ post.content | strip_html | normalize_whitespace | truncate: 150 | jsonify }}
    }{% unless forloop.last %},{% endunless %}
  {% endfor %}
  ]
};
