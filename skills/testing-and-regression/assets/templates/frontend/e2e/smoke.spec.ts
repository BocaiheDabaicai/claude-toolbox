import { expect, test } from '@playwright/test'

// 示例：只测关键链路。按项目替换选择器和步骤。
test('login page renders', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('form')).toBeVisible()
  await expect(page.getByRole('button', { name: /登录/ })).toBeVisible()
})

test('critical flow: login -> first page', async ({ page }) => {
  await page.goto('/')

  // 推荐给关键元素加 data-testid，避免依赖文案/结构。
  await page.getByLabel(/邮箱|账号/).fill(process.env.E2E_USER || 'admin@example.com')
  await page.getByLabel(/密码/).fill(process.env.E2E_PASSWORD || 'password')
  await page.getByRole('button', { name: /登录/ }).click()

  await expect(page).not.toHaveURL(/login/)
  await expect(page.locator('main')).toBeVisible()
})
