#!/usr/bin/env python3
"""
Starrope Finance Blog - 자동 예약 발행 스크립트
GitHub Actions에서 KST 오전 8시, 오후 4시에 실행
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta

# KST = UTC+9
KST = timezone(timedelta(hours=9))

def get_current_kst():
    """현재 KST 시간 반환"""
    return datetime.now(timezone.utc).astimezone(KST)

def get_time_slot(hour):
    """현재 시간이 오전/오후 슬롯인지 판단"""
    if 0 <= hour < 12:
        return '08:00'
    else:
        return '16:00'

def generate_card_html(post):
    """포스트 메타데이터로 카드 HTML 생성"""
    return f"""         <!-- Post: {post['filename']} -->
         <article class="post-card">
           <div class="post-card-thumb" style="background-image: url('{post['image_url']}');">
             <span class="post-tag">{post['tag']}</span>
           </div>
           <div class="post-card-content">
             <div class="post-meta">
               <span>작성자: Starrope</span>
               <span>•</span>
               <span>{post['date_display']}</span>
             </div>
             <h3 class="post-card-title"><a href="posts/{post['filename']}">{post['title']}</a></h3>
             <p class="post-card-desc">{post['description']}</p>
             <div class="post-card-footer">
               <a href="posts/{post['filename']}" class="read-more-btn">
                 읽어보기 
                 <svg xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
                 </svg>
               </a>
             </div>
           </div>
         </article>
"""

def is_already_published(filename, index_content):
    """index.html에 이미 해당 포스트 카드가 있는지 확인"""
    return f'posts/{filename}' in index_content

def insert_card_to_index(card_html, index_content):
    """index.html의 SCHEDULED_POSTS_START 마커 바로 뒤에 카드 삽입"""
    marker = '<!-- SCHEDULED_POSTS_START -->'
    if marker not in index_content:
        print("경고: SCHEDULED_POSTS_START 마커를 찾을 수 없습니다.")
        return index_content
    return index_content.replace(
        marker,
        marker + '\n' + card_html,
        1
    )

def add_url_to_sitemap(filename, publish_date, sitemap_content):
    """sitemap.xml에 새 URL 추가"""
    if f'posts/{filename}' in sitemap_content:
        return sitemap_content
        
    new_url = f"""  <url>
    <loc>https://blog3.starrope2023.com/posts/{filename}</loc>
    <lastmod>{publish_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
"""
    return sitemap_content.replace('</urlset>', new_url + '</urlset>')

def main():
    now = get_current_kst()
    today = now.date()
    current_hour = now.hour
    time_slot = get_time_slot(current_hour)

    print(f"현재 KST 시간: {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"발행 슬롯: {time_slot}")

    # schedule.json 읽기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    with open(os.path.join(project_root, 'schedule.json'), 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    # index.html & sitemap.xml 읽기
    index_path = os.path.join(project_root, 'index.html')
    sitemap_path = os.path.join(project_root, 'sitemap.xml')

    with open(index_path, 'r', encoding='utf-8') as f:
        index_content = f.read()

    with open(sitemap_path, 'r', encoding='utf-8') as f:
        sitemap_content = f.read()

    published_count = 0

    for post in schedule['posts']:
        post_date_str = post['publish_date']
        post_time = post['publish_time']
        post_date = datetime.strptime(post_date_str, '%Y-%m-%d').date()

        # 이미 발행된 포스트는 스킵
        if is_already_published(post['filename'], index_content):
            continue

        # 발행 조건 확인: 오늘 이전 날짜 또는 오늘의 해당 슬롯 시간
        should_publish = False

        if post_date < today:
            # 놓친 이전 날짜 포스트 - 이번 실행에서 발행
            should_publish = True
        elif post_date == today:
            # 오늘 날짜: 해당 슬롯 시간이 됐는지 확인
            post_hour = 8 if post_time == '08:00' else 16
            if current_hour >= post_hour:
                should_publish = True

        if should_publish:
            filename = post['filename']
            print(f"발행 중: {filename} ({post_date_str} {post_time})")

            # 카드 HTML 생성 후 index.html에 삽입
            card_html = generate_card_html(post)
            index_content = insert_card_to_index(card_html, index_content)

            # sitemap.xml에 URL 추가
            sitemap_content = add_url_to_sitemap(filename, post_date_str, sitemap_content)

            published_count += 1

    if published_count > 0:
        print(f"\n총 {published_count}개 포스트 발행 완료!")

        # index.html 저장
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        print("index.html 업데이트 완료")

        # sitemap.xml 저장
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        print("sitemap.xml 업데이트 완료")
    else:
        print("발행할 포스트가 없습니다.")

if __name__ == '__main__':
    main()
