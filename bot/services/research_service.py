import aiohttp
from bs4 import BeautifulSoup
from bot.services.ai_service import AIService


class ResearchService:
    def __init__(self):
        self.ai = AIService()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
        }

    async def research(self, topic: str, style: str = "structured") -> str:
        web_context = await self._fetch_web_context(topic)
        messages = [{
            "role": "user",
            "content": f"""Research topic: {topic}

Web context gathered:
{web_context}

Provide a comprehensive research report with:
1. **Executive Summary**
2. **Background & Context** 
3. **Key Findings & Facts**
4. **Current Developments (2024-2025)**
5. **Expert Perspectives**
6. **Implications & Applications**
7. **Conclusion**

Be thorough, accurate, and insightful."""
        }]
        return await self.ai.chat(messages, style=style)

    async def _fetch_web_context(self, topic: str) -> str:
        try:
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={topic}&format=json&srlimit=3"
            async with aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(search_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("query", {}).get("search", [])
                        context = f"Wikipedia search for '{topic}':\n"
                        for r in results[:2]:
                            context += f"- {r['title']}: {BeautifulSoup(r.get('snippet', ''), 'html.parser').get_text()}\n"
                        return context
        except Exception:
            pass
        return f"Research topic: {topic} (web context unavailable, using training knowledge)"
