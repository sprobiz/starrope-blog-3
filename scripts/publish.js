const fs = require('fs');
const path = require('path');

const projectRoot = path.join(__dirname, '..');
const schedulePath = path.join(projectRoot, 'schedule.json');
const indexPath = path.join(projectRoot, 'index.html');
const sitemapPath = path.join(projectRoot, 'sitemap.xml');

const schedule = JSON.parse(fs.readFileSync(schedulePath, 'utf8'));
let indexContent = fs.readFileSync(indexPath, 'utf8');
let sitemapContent = fs.readFileSync(sitemapPath, 'utf8');

const today = new Date().toISOString().split('T')[0]; // KST / UTC date check
console.log(`Current Date: ${today}`);

function generateCardHtml(post) {
  return `         <!-- Post: ${post.filename} -->
         <article class="post-card">
           <div class="post-card-thumb" style="background-image: url('${post.image_url}');">
             <span class="post-tag">${post.tag}</span>
           </div>
           <div class="post-card-content">
             <div class="post-meta">
               <span>작성자: Starrope</span>
               <span>•</span>
               <span>${post.date_display}</span>
             </div>
             <h3 class="post-card-title"><a href="posts/${post.filename}">${post.title}</a></h3>
             <p class="post-card-desc">${post.description}</p>
             <div class="post-card-footer">
               <a href="posts/${post.filename}" class="read-more-btn">
                 읽어보기 
                 <svg xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
                 </svg>
               </a>
             </div>
           </div>
         </article>
`;
}

let publishedCount = 0;

for (const post of schedule.posts) {
  const filename = post.filename;
  if (indexContent.includes(`posts/${filename}`)) {
    continue;
  }

  // Check publish date
  if (post.publish_date <= today) {
    console.log(`Publishing: ${filename} (${post.publish_date} ${post.publish_time})`);

    const cardHtml = generateCardHtml(post);
    const marker = '<!-- SCHEDULED_POSTS_START -->';
    if (indexContent.includes(marker)) {
      indexContent = indexContent.replace(marker, marker + '\n' + cardHtml);
    } else {
      console.warn('Warning: SCHEDULED_POSTS_START marker not found');
    }

    if (!sitemapContent.includes(`posts/${filename}`)) {
      const newUrl = `  <url>
    <loc>https://blog3.starrope2023.com/posts/${filename}</loc>
    <lastmod>${post.publish_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
`;
      sitemapContent = sitemapContent.replace('</urlset>', newUrl + '</urlset>');
    }

    publishedCount++;
  }
}

if (publishedCount > 0) {
  fs.writeFileSync(indexPath, indexContent, 'utf8');
  console.log('Updated index.html');
  fs.writeFileSync(sitemapPath, sitemapContent, 'utf8');
  console.log('Updated sitemap.xml');
  console.log(`Successfully published ${publishedCount} post(s)!`);
} else {
  console.log('No new posts to publish.');
}
