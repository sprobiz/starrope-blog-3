const fs = require('fs');
const path = require('path');

const schedulePath = path.join(__dirname, 'schedule.json');
const schedule = JSON.parse(fs.readFileSync(schedulePath, 'utf8'));

const newPost = {
  "filename": "earned-income-tax-credit-2026.html",
  "title": "2026년 근로장려금 하반기 반기 신청기간 및 지급액 총정리: 최대 330만원 가이드",
  "description": "2026년 근로장려금 하반기 반기 신청기간, 지급일, 가구원 및 소득·재산 자격조건을 총정리합니다. 1인 가구, 맞벌이 가구별 최대 330만 원 지급액을 확인하세요.",
  "image_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
  "tag": "정부지원금 / 세테크",
  "date_display": "2026. 10. 05",
  "publish_date": "2026-10-05",
  "publish_time": "12:00:00"
};

schedule.posts.unshift(newPost);

fs.writeFileSync(schedulePath, JSON.stringify(schedule, null, 2), 'utf8');
console.log('schedule.json updated successfully.');
