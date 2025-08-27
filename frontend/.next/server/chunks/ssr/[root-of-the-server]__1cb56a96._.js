module.exports = [
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>NewsCard
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/cording/git/NewsFlow_AI/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
;
// 신뢰도 등급에 따른 색상 클래스를 반환하는 함수
const getReliabilityClass = (reliabilityClass)=>{
    switch(reliabilityClass){
        case 'high':
            return 'bg-blue-100 text-blue-800';
        case 'medium':
            return 'bg-yellow-100 text-yellow-800';
        case 'low':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
};
// 날짜 형식을 'YYYY.MM.DD HH:mm'으로 변환하는 함수
const formatDate = (dateString)=>{
    if (!dateString) return '날짜 정보 없음';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '유효하지 않은 날짜';
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}.${month}.${day} ${hours}:${minutes}`;
};
function NewsCard({ news }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("a", {
        href: news.link,
        target: "_blank",
        rel: "noopener noreferrer",
        className: "block h-full",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("article", {
            className: "bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full flex flex-col",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "p-4 flex flex-col flex-grow",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex justify-between items-start mb-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "font-semibold text-sm text-gray-700",
                                children: news.source
                            }, void 0, false, {
                                fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
                                lineNumber: 37,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: `px-2 py-1 text-xs font-bold rounded-full ${getReliabilityClass(news.reliability_class)}`,
                                children: [
                                    "신뢰도: ",
                                    news.reliability
                                ]
                            }, void 0, true, {
                                fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
                                lineNumber: 40,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
                        lineNumber: 36,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                        className: "font-bold text-md mb-2 text-gray-900 line-clamp-2 h-12",
                        children: news.title
                    }, void 0, false, {
                        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
                        lineNumber: 47,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-gray-600 text-sm line-clamp-3 mb-4 flex-grow",
                        children: news.summary
                    }, void 0, false, {
                        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
                        lineNumber: 51,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "text-right text-xs text-gray-500 mt-auto pt-2 border-t",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("time", {
                            dateTime: news.date,
                            children: formatDate(news.date)
                        }, void 0, false, {
                            fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
                            lineNumber: 56,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
                        lineNumber: 55,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
                lineNumber: 35,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
            lineNumber: 34,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx",
        lineNumber: 33,
        columnNumber: 5
    }, this);
}
}),
"[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>NewsSection
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/cording/git/NewsFlow_AI/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/cording/git/NewsFlow_AI/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$frontend$2f$src$2f$components$2f$NewsCard$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsCard.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
const CATEGORIES = [
    '정치',
    '경제',
    '사회',
    'IT/기술',
    '생활_문화',
    '세계'
];
const TRUSTED_SOURCES = [
    "조선일보",
    "한겨레",
    "중앙일보",
    "동아일보",
    "경향신문"
]; // 신뢰도 평가 기준 언론사
function NewsSection() {
    const [selectedCategory, setSelectedCategory] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('정치');
    const [newsData, setNewsData] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const fetchNews = async ()=>{
            setIsLoading(true);
            setError(null);
            setNewsData([]); // 카테고리 변경 시 기존 데이터 초기화
            try {
                const response = await fetch(`http://127.0.0.1:8000/api/analyze`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        categories: [
                            selectedCategory
                        ],
                        trusted_sources: TRUSTED_SOURCES
                    })
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || '뉴스 데이터를 불러오는 데 실패했습니다.');
                }
                const data = await response.json();
                setNewsData(data);
            } catch (err) {
                setError(err.message);
            } finally{
                setIsLoading(false);
            }
        };
        fetchNews();
    }, [
        selectedCategory
    ]); // selectedCategory가 변경될 때마다 API 호출
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        className: "bg-gray-50 pt-8 pb-12",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                className: "bg-white py-3 border-b shadow-sm px-8 sticky top-0 z-10",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("ul", {
                    className: "flex justify-center space-x-8 font-semibold",
                    children: CATEGORIES.map((category)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                onClick: ()=>setSelectedCategory(category),
                                className: `pb-1 hover:text-blue-600 transition-colors duration-200 ${selectedCategory === category ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`,
                                children: category.replace('_', '/')
                            }, void 0, false, {
                                fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                                lineNumber: 64,
                                columnNumber: 15
                            }, this)
                        }, category, false, {
                            fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                            lineNumber: 63,
                            columnNumber: 13
                        }, this))
                }, void 0, false, {
                    fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                    lineNumber: 61,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                lineNumber: 60,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "px-8 mt-8",
                children: isLoading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "text-center py-20",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-lg font-semibold text-gray-600",
                        children: "AI가 뉴스를 분석하고 있습니다..."
                    }, void 0, false, {
                        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                        lineNumber: 82,
                        columnNumber: 13
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                    lineNumber: 81,
                    columnNumber: 11
                }, this) : error ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "text-center py-20",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-lg font-semibold text-red-600",
                        children: [
                            "오류: ",
                            error
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                        lineNumber: 86,
                        columnNumber: 13
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                    lineNumber: 85,
                    columnNumber: 11
                }, this) : newsData.map((section, index)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                        className: "mb-12",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                                className: "text-2xl font-bold mb-4 text-gray-800 border-l-4 border-blue-600 pl-3",
                                children: section.sub_category
                            }, void 0, false, {
                                fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                                lineNumber: 91,
                                columnNumber: 15
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6",
                                children: section.articles.map((news, newsIndex)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$cording$2f$git$2f$NewsFlow_AI$2f$frontend$2f$src$2f$components$2f$NewsCard$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                        news: news
                                    }, newsIndex, false, {
                                        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                                        lineNumber: 96,
                                        columnNumber: 19
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                                lineNumber: 94,
                                columnNumber: 15
                            }, this)
                        ]
                    }, index, true, {
                        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                        lineNumber: 90,
                        columnNumber: 13
                    }, this))
            }, void 0, false, {
                fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
                lineNumber: 79,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Documents/cording/git/NewsFlow_AI/frontend/src/components/NewsSection.tsx",
        lineNumber: 59,
        columnNumber: 5
    }, this);
}
}),
"[project]/Documents/cording/git/NewsFlow_AI/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
;
else {
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    else {
        if ("TURBOPACK compile-time truthy", 1) {
            if ("TURBOPACK compile-time truthy", 1) {
                module.exports = __turbopack_context__.r("[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)");
            } else //TURBOPACK unreachable
            ;
        } else //TURBOPACK unreachable
        ;
    }
} //# sourceMappingURL=module.compiled.js.map
}),
"[project]/Documents/cording/git/NewsFlow_AI/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

module.exports = __turbopack_context__.r("[project]/Documents/cording/git/NewsFlow_AI/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)").vendored['react-ssr'].ReactJsxDevRuntime; //# sourceMappingURL=react-jsx-dev-runtime.js.map
}),
"[project]/Documents/cording/git/NewsFlow_AI/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

module.exports = __turbopack_context__.r("[project]/Documents/cording/git/NewsFlow_AI/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)").vendored['react-ssr'].React; //# sourceMappingURL=react.js.map
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__1cb56a96._.js.map