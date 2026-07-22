import asyncio
import time
import httpx

# TODO 1: Write an async function `fetch_user(client, username)` that uses
# client.get() (await it) to hit https://api.github.com/users/{username}
# and returns the parsed JSON dict


async def fetch_user(client: httpx.AsyncClient, username: str) -> dict:
    start = time.perf_counter()
    response = await client.get(f"https://api.github.com/users/{username}")
    data = response.json()

    print(response.status_code)
    end = time.perf_counter()
    elapsed = end - start
    print(f"Took {elapsed: .2f} seconds")
    return data


# TODO 2: Write an async function `main()` that:
#   - opens one httpx.AsyncClient() using `async with`
#   - fetches THREE users concurrently using asyncio.gather()
#     (try: "octocat", "torvalds", "gvanrossum")
#   - prints each user's login and public_repos count


async def main():
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch_user(client, "octocat"),
            fetch_user(client, "torvalds"),
            fetch_user(client, "gvanrossum"),
        )
        for result in results:
            print(result["login"], result["public_repos"])
    end = time.perf_counter()
    elapsed_concurrent = end - start
    print(f"Concurrent: {elapsed_concurrent:.2f}s")


asyncio.run(main())

# TODO 3: Run main() with asyncio.run()

# BONUS: add a simple timer (time.perf_counter() before/after) around the
# gather() call, and compare it mentally to calling fetch_user three times
# sequentially with plain httpx.get() - this is where async concurrency
# actually pays off, same lesson as CompletableFuture.allOf() vs sequential .get()
