import asyncio
import logging
import time

from x_model import init_db
from xync_schema import models
from xync_client.loader import TORM
from camoufox.async_api import AsyncCamoufox

logging.basicConfig(level=logging.INFO)


async def _input(page):
    for i in input("Login: "):
        await page.keyboard.press(i)
    await page.wait_for_timeout(1000)


async def payment(page, agent, account, amount, cur):
    await page.goto("https://payeer.com/en/account/send/")
    fiat_accounts = await page.locator(
        f".balance-item.balance-item--green.balance-item--{cur.lower()}"
    ).all_text_contents()
    if float(amount) <= float(fiat_accounts[0].replace(",", "").strip()):
        await page.locator('input[name="param_ACCOUNT_NUMBER"]').fill(account)
        time.sleep(1)
        await page.locator('.jq-selectbox__select-text:has-text("USD")').first.click()
        time.sleep(1)
        await page.locator(f'li:has-text("{cur}")').first.click()
        time.sleep(1)
        await page.locator('input[name="sum_receive"]').fill(amount)
        time.sleep(1)
        await page.click(".btn.n-form--btn.n-form--btn-mod")
        time.sleep(1)
        await page.click(".btn.n-form--btn.n-form--btn-mod")
        time.sleep(1)
        if await page.locator(".input4").count():
            await page.locator(".input4").fill(agent.auth.get("master_key"))
            time.sleep(1)
            await page.click(".ok.button_green2")
        time.sleep(2)
        await page.locator(".note_txt").wait_for(state="visible")
        if await page.locator('.note_txt:has-text("successfully completed")').count():
            transaction = await page.locator(".note_txt").all_text_contents()
            number_transaction = transaction[0].replace("Transaction #", "").split()[0]
            await page.goto("https://payeer.com/ru/account/history/")
            await page.click(f".history-id-{number_transaction} a.link")
            time.sleep(1)
            receipt = await page.query_selector(".ui-dialog.ui-corner-all")
            time.sleep(1)
            await receipt.screenshot(path="screen.png")
            logging.info(f"Payeer sent {amount}{cur} to {account}")
        else:
            print("какая то ошибка")
    else:
        logging.error(f"Payeer no have {amount}, only {fiat_accounts[0].strip()}{cur} to {account}")


async def main(account, amount, cur):
    _ = await init_db(TORM, True)
    agent = await models.PmAgent.filter(pm__norm="payeer", auth__isnull=False).first()
    async with AsyncCamoufox(os=["macos"], headless=False) as playwright:
        context = await playwright.new_context(storage_state=agent.state, record_video_dir="videos")
        page = await context.new_page()
        # await page.wait_for_timeout(15000)
        await page.goto("https://payeer.com/en/", wait_until="domcontentloaded", timeout=60000)
        try:
            if await page.locator('.btn.btn--create:has-text("Create Account")').count():
                agent.state = {}
                await asyncio.sleep(1)
                await page.click(".btn.btn--login.white-login")
                time.sleep(1)
                await page.locator('input[name="email"]').fill(agent.auth.get("email"))
                time.sleep(1)
                await page.locator('input[name="password"]').fill(agent.auth.get("passwd"))
                time.sleep(1)
                await page.locator(".login-form__login-btn.step1").click()
                time.sleep(7)
                if await page.locator(".login-form__login-btn.step1").is_visible():
                    await page.click(".login-form__login-btn.step1", timeout=7000)
                time.sleep(1)
                if await page.locator('.form-input-top:has-text("Enter the verification code")').count():
                    await _input(page)
                    await page.click(".login-form__login-btn.step2")
                agent.state = await page.context.storage_state()
                await agent.save()
                time.sleep(5)
            await payment(page, agent, account, amount, cur)
        finally:
            await playwright.close()


if __name__ == "__main__":
    import sys

    _, account, amount, *__ = sys.argv
    asyncio.run(main(account, amount, __ and __[0] or "RUB"))
