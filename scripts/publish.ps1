$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

$schedulePath = Join-Path $projectRoot "schedule.json"
$indexPath = Join-Path $projectRoot "index.html"
$sitemapPath = Join-Path $projectRoot "sitemap.xml"

$schedule = Get-Content -Raw -Encoding UTF8 $schedulePath | ConvertFrom-Json
$indexContent = [System.IO.File]::ReadAllText($indexPath, [System.Text.Encoding]::UTF8)
$sitemapContent = [System.IO.File]::ReadAllText($sitemapPath, [System.Text.Encoding]::UTF8)

$today = (Get-Date).ToString("yyyy-MM-dd")
Write-Host "Current Date: $today"

$publishedCount = 0

foreach ($post in $schedule.posts) {
    $fn = $post.filename
    if ($indexContent.Contains("posts/$fn")) {
        continue
    }

    if ($post.publish_date -le $today) {
        Write-Host "Publishing: $fn ($($post.publish_date) $($post.publish_time))"
        
        $card = @"
         <!-- Post: $fn -->
         <article class="post-card">
           <div class="post-card-thumb" style="background-image: url('$($post.image_url)');">
             <span class="post-tag">$($post.tag)</span>
           </div>
           <div class="post-card-content">
             <div class="post-meta">
               <span>작성자: Starrope</span>
               <span>•</span>
               <span>$($post.date_display)</span>
             </div>
             <h3 class="post-card-title"><a href="posts/$fn">$($post.title)</a></h3>
             <p class="post-card-desc">$($post.description)</p>
             <div class="post-card-footer">
               <a href="posts/$fn" class="read-more-btn">
                 읽어보기 
                 <svg xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
                 </svg>
               </a>
             </div>
           </div>
         </article>
"@

        $marker = "<!-- SCHEDULED_POSTS_START -->"
        if ($indexContent.Contains($marker)) {
            $indexContent = $indexContent.Replace($marker, "$marker`n$card")
        } else {
            Write-Warning "SCHEDULED_POSTS_START marker not found"
        }

        if (-not $sitemapContent.Contains("posts/$fn")) {
            $newUrl = @"
  <url>
    <loc>https://blog3.starrope2023.com/posts/$fn</loc>
    <lastmod>$($post.publish_date)</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
"@
            $sitemapContent = $sitemapContent.Replace("</urlset>", "$newUrl`n</urlset>")
        }

        $publishedCount++
    }
}

if ($publishedCount -gt 0) {
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($indexPath, $indexContent, $utf8NoBOM)
    Write-Host "Updated index.html"
    [System.IO.File]::WriteAllText($sitemapPath, $sitemapContent, $utf8NoBOM)
    Write-Host "Updated sitemap.xml"
    Write-Host "Successfully published $publishedCount post(s)!"
} else {
    Write-Host "No new posts to publish."
}
