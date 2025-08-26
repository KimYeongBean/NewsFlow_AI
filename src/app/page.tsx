import NewsCard from '@/components/NewsCard';

// NewsArticle 타입 정의 (별도 파일로 분리 권장)
type NewsArticle = {
  id: number;
  imageSrc: string;
  publisher: string;
  title: string;
  description: string;
  link: string;
  publishedDate: string;
};

// 12개의 뉴스 데이터를 반환하는 비동기 함수
async function getNewsData(): Promise<NewsArticle[]> {
  const newsData = [
    {
      id: 1,
      title: '“경제 위해 美 가장 중요” 1년새 55%→70%…이젠 ‘안미경미’?',
      publisher: '헤럴드경제',
      link: 'https://news.google.com/rss/articles/CBMiVkFVX3lxTE9sRDhoVGRVM3BYLVA2bDRlQUVneVVHeGdWU3Rna0JiR3M3SE8zNlBmRFoxNTVCN0NSeWlZaWVtc0xOaHZpd3N5TTRBaFM1QmRZaVdlbEdR?oc=5',
      publishedDate: '2025-08-22 15:00:00',
      imageSrc: '/news-images/economy-1.jpg',
      description: '우리나라 경제를 위해 가장 중요한 협력 파트너로 미국을 꼽는 국민이 1년 새 크게 늘어난 것으로 나타났다.',
    },
    {
      id: 2,
      title: '해외 기업인 입국심사 빨라진다…“경제 활성화 기대”',
      publisher: '한겨레',
      link: 'https://news.google.com/rss/articles/CBMickFVX3lxTFBNREQzQk9rWk9YUV96VEFvRHotUWJiRUZVMks5X185eVEwcnh0RXpyMGdVa3BoT2V6Q2NhNTQxRDdmS2ZKcS12OUJ6VXJVSkpBdVg1VzhyNmdiWHE5cHl4SGZFR1E4dmNNMHdQN3lVbml3dw?oc=5',
      publishedDate: '2025-08-26 02:00:00',
      imageSrc: '/news-images/economy-2.jpg',
      description: '정부가 해외 기업인의 입국 절차를 간소화하여 국내 투자 및 경제 활성화를 도모할 계획이라고 밝혔다.',
    },
    {
      id: 3,
      title: '이념 우선 경제정책… ‘李대통령 말’보다 ‘정청래 행동’이 앞서간다',
      publisher: '조선일보',
      link: 'https://news.google.com/rss/articles/CBMijgFBVV95cUxQSjJ5RE4wUGU1blVHWGRpdWJoRlNFczdyMHhXR0FOSHp6bnpRWmdHRFFNcXpUMDhFS2JRdndOY2xXQnNCaHdZcEhROURkNDVRVHEyWmMwbmMtZ2hOZjJ1MDhzbTZVNnY4WlB0ZE5mM0NkUzVra0hmMmZiSjBncE1SVmx6X1Zpa3hVbUJCVE1n0gGiAUFVX3lxTE5ZNzdhODVYOXpyWTBHNXJ0bUNrT1E2RDU0TmNJa1lINWhER1Q2RTB3YnVaMlNoNW5YcEtDZTQzN2JVVkxvOG92RUZXNDlUdTlDOTRtdmtmUjN0WUQ2ODVzSGQzUy1sWXo2SmN4blFseTVCcTFOMS1VRDV1V21ZNGZjRlptWnhYSHk4eDZOeDZ2Y3dEU2R1ZkxRNDVzVDlYMWx3Zw?oc=5',
      publishedDate: '2025-08-24 16:00:56',
      imageSrc: '/news-images/politics-1.jpg',
      description: '최근 정부의 경제 정책 방향이 실용보다는 이념적 잣대에 치우치고 있다는 비판이 제기되고 있다.',
    },
    {
      id: 4,
      title: '한·호쿠리쿠 경제교류회의 개최…지역 산업·탄소중립 협력 논의',
      publisher: '뉴스1',
      link: 'https://news.google.com/rss/articles/CBMiY0FVX3lxTFBlcGRKbkJnODE0X2tyZDNhVDk0bWlxV0VxVVNkMUI4cTR2TkF2Rk54NFRpZjdUMG5WR1p2MThGbkM1a05jVUl2LXZ0ZzU4eURVd1FRQVdWSkZCYU8xdmxrYk5wOA?oc=5',
      publishedDate: '2025-08-25 21:00:00',
      imageSrc: '/news-images/economy-3.jpg',
      description: '한국과 일본 호쿠리쿠 지역 기업인들이 모여 지역 산업 발전과 탄소 중립 목표 달성을 위한 협력 방안을 논의했다.',
    },
    {
      id: 5,
      title: '해고 안하지만 뽑지도 않는다…노동시장, 미국 경제 뇌관 되나',
      publisher: '연합뉴스',
      link: 'https://news.google.com/rss/articles/CBMiW0FVX3lxTFBEanlOVnJlUW4yZE1qeEgwVE9WYnprNGxYVDB1RjdXUU9Tb01PQXJWeUk1QlRBSDlhUnoyZkJfR0lzaXpnWGpmcEdPWmFyVjNfUl8tYThodUtGUEnSAWBBVV95cUxQQWRDMzdqMkowZEVUc1lUVUxXYVpteTNZWVBTbzRmVTh1NG5EVV9kQlJFbUpyTlEtVEk2ZmMyUEVucEJieDVadGZMRU9qUFRpM2RoOEFfNGd1N2pLZzVZYnE?oc=5',
      publishedDate: '2025-08-25 01:16:45',
      imageSrc: '/news-images/world-1.jpg',
      description: '미국 노동 시장에서 해고율은 낮지만 신규 채용이 줄어드는 현상이 나타나며 경제에 불안 요소로 작용하고 있다.',
    },
    {
      id: 6,
      title: '이재명 정부 첫 방미 경제사절단, \'실용 노선\'으로 \'K광물\' 넣고 \'철강\' 빠지고',
      publisher: '비즈니스포스트',
      link: 'https://news.google.com/rss/articles/CBMic0FVX3lxTE1kbkp1bU5ac04tdnZWQkhMZDJ6aEJXZVVIUHRXSU5mR2Q0WU5tVnlFanZ0RlhXWVp2ZmFBVlFfWjZYb1RtNnRha3M2QWo2NllCTFVqLThaaEh1a3lHdTBxRk1Fcm5fdzY2ZFlnZFlGaTg2OEE?oc=5',
      publishedDate: '2025-08-25 01:54:23',
      imageSrc: '/news-images/politics-2.jpg',
      description: '정부의 첫 미국 파견 경제사절단 구성에서 핵심 광물 관련 기업이 포함되고 철강 기업이 제외되어 정책 변화를 시사했다.',
    },
    {
      id: 7,
      title: '경제8단체 “2차 상법 개정안 통과 유감”',
      publisher: '채널A',
      link: 'https://news.google.com/rss/articles/CBMifkFVX3lxTE9KUlRYakR0VW4tSTJEUy1CQXRUeEpMVE9fNE43U04tTHN5a0dDWS1HRHpfUW9nS1U5VTBacDNESXNLVVA4M01jMTh5d1hidWZJU0JVb0kyRTNvQmxONGluRlEwZzlwUVFFVENBc2NvQ19rZE43OXFYeW45RzREUdIBgwFBVV95cUxNTDBWRXpxVUIwdTRaQ2I2Ny1KckNhTkFZaHZpUG1WVGZjSUZEWTZDN1ZfM0tEakxMRHBIVW9HN3BGbDRXRy10OHVRZEJGdUprX2ZfTUUwTjlDVl9CbXJXUEtJdEt2cHZUdHVDa0xPTElyLUoxUzJRaTlrUFFXSWNEZEJ5aw?oc=5',
      publishedDate: '2025-08-25 02:27:00',
      imageSrc: '/news-images/economy-4.jpg',
      description: '주요 경제 단체들이 이사회 의무 강화 등을 담은 상법 개정안의 국회 통과에 대해 경영권 위축을 우려하며 유감을 표명했다.',
    },
    {
      id: 8,
      title: '더 센 상법 여당 주도 본회의 통과…국힘 경제 내란',
      publisher: 'MBN 홈페이지',
      link: 'https://news.google.com/rss/articles/CBMiVkFVX3lxTE85eW9kclBYWkktRGljcmM3eUVRMk1BdDVRMEJ0NzZtWmhNNWthN2x5bFBSQmEwRTI3bzREVW9FdURaQi02Q1JDMGk2TWlrOURjVEVNUTlR0gFMQVVfeXFMT25YWjFybm1wSVhSU3VrQ0t2US1BRlNYY0R3ck1EM2xTTFE2elFmbVByTXVSSDVrM0J2ZGlkWm1pUDRkeUNBbXNkX0lVZw?oc=5',
      publishedDate: '2025-08-25 22:59:35',
      imageSrc: '/news-images/politics-3.jpg',
      description: '여당이 단독으로 처리한 상법 개정안에 대해 야당은 \'경제 내란\'이라며 강하게 반발하며 정국이 급랭하고 있다.',
    },
    {
      id: 9,
      title: '‘집중투표제’에 ‘감사위원 분리선출’까지 [알기쉬운 경제]',
      publisher: '쿠키뉴스',
      link: 'https://news.google.com/rss/articles/CBMiY0FVX3lxTE1SWFVUOEF5LUJ5SHI1N3l6UzA5bVFhekJhTGczc2t2Zm9MSU5keFh5ckxLaVJtZ19nSVU1aEJzcWxiR0dtUGsyNmlNNmllOF83M01XRGdQQ05rVl84SUlHdE0xbw?oc=5',
      publishedDate: '2025-08-25 21:00:08',
      imageSrc: '/news-images/economy-5.jpg',
      description: '새로운 상법 개정안의 핵심인 집중투표제와 감사위원 분리선출 제도가 소액주주 권익 보호에 미칠 영향을 분석한다.',
    },
    {
      id: 10,
      title: '외교장관과 경제장관의 \'경솔한 입\'',
      publisher: '프레시안',
      link: 'https://news.google.com/rss/articles/CBMia0FVX3lxTFBxdTVoZ2dwekI5QU9Xb1FPcERkUVgxTFppanZkSFE2aG9SNTFzQ3NqaG1tNkphVDd4ZWVUNDJqa1UtTnpUMzdtMmZOU2NkZ2k3dHV5Q1lIWlVaa01ST0djV0hUTE1hTVBkUFRZ?oc=5',
      publishedDate: '2025-08-25 00:21:09',
      imageSrc: '/news-images/politics-4.jpg',
      description: '최근 외교부와 경제부처 수장의 발언이 연이어 논란을 일으키며 정부의 신뢰도에 타격을 주고 있다는 지적이 나온다.',
    }
  ];
  return newsData;
}


export default async function NewsHomepage() {
  const newsData = await getNewsData();

  return (
    <>
      {/* Header, Banner, Nav 등 다른 섹션은 기존과 동일합니다. */}
      <header className="bg-white py-4 flex items-center justify-between px-8 border-b">
        <h1 className="text-2xl font-extrabold text-blue-600">NEWS FLOW</h1>
        <div className="relative">
          <input type="text" placeholder="뉴스 검색..." className="border rounded-full py-2 px-4 w-64" />
          <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
            🔍
          </button>
        </div>
      </header>
      
      <section className="relative h-64 bg-blue-800 overflow-hidden">
        <div className="absolute bottom-8 left-8 text-white">
          <div className="uppercase text-sm mb-2">Top</div>
          <h2 className="text-3xl font-bold mb-4">BREAKING NEWS</h2>
          <p className="text-sm">트래픽 급증! 실시간 속보</p>
          <button className="bg-yellow-400 text-black font-bold py-2 px-4 rounded-md mt-2 hover:bg-yellow-300">자세히 보기</button>
        </div>
      </section>

      <nav className="bg-white py-3 border-b shadow-sm">
        <ul className="flex justify-center space-x-8 font-semibold text-gray-600">
          <li><a href="#" className="hover:text-blue-600">경제</a></li>
          <li><a href="#" className="hover:text-blue-600">사회</a></li>
          <li><a href="#" className="hover:text-blue-600">정치</a></li>
          <li><a href="#" className="hover:text-blue-600">IT/기술</a></li>
          <li><a href="#" className="hover:text-blue-600">문화</a></li>
        </ul>
      </nav>
      
      <main className="bg-gray-50 p-8">
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {newsData.map((news) => (
            <a
              href={news.link}
              key={news.id}
              target="_blank"
              rel="noopener noreferrer"
              className="block"
            >
              <NewsCard news={news} />
            </a>
          ))}
        </section>

        <section className="mt-12">
          <h2 className="text-2xl font-bold mb-4 text-center">언론사별 뉴스</h2>
          {/* 언론사별 뉴스 콘텐츠 */}
        </section>
      </main>

      <footer className="bg-gray-800 py-6 px-8 text-center text-gray-400">
        <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row justify-between items-center">
          <ul className="flex space-x-6 mb-4 md:mb-0">
            <li><a href="#" className="hover:text-white">회사소개</a></li>
            <li><a href="#" className="hover:text-white">연락처</a></li>
            <li><a href="#" className="hover:text-white">개인정보보호정책</a></li>
          </ul>
          <div className="text-gray-500">
            © 2025 News Flow. All Rights Reserved.
          </div>
        </div>
      </footer>
    </>
  );
}