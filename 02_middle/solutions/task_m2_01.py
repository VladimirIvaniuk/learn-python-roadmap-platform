"""
Рішення — Урок 2 (Async)

Дивись після того, як спробував сам!
"""
import asyncio


async def delay_print(text: str, seconds: float) -> None:
    await asyncio.sleep(seconds)
    print(text)


async def fetch_all(urls: list[str]) -> list[str]:
    async def fetch(url: str) -> str:
        await asyncio.sleep(0.5)
        return f"Data from {url}"

    return await asyncio.gather(*[fetch(u) for u in urls])


async def main() -> None:
    await asyncio.gather(
        delay_print("First", 0.3),
        delay_print("Second", 0.1),
        delay_print("Third", 0.2),
    )
    results = await fetch_all(["a.com", "b.com"])
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
