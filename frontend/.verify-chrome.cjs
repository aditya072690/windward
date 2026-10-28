const { chromium } = require('playwright')

const URL = 'http://localhost:5175/'
const OUT = '/private/var/folders/cc/v6dtqkmd4bg3721nfmp509_c0000gn/T/opencode'

async function main() {
  const browser = await chromium.launch({ channel: 'chrome' })
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } })
  const errors = []
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text())
  })
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message))

  await page.goto(URL, { waitUntil: 'networkidle' })
  await page.waitForSelector('#day')
  await page.getByRole('radio', { name: 'Decision-time' }).click()
  await page.waitForTimeout(300)

  const measure = () =>
    page.evaluate(() => {
      const q = (s) => document.querySelector(s)
      const range = q('#cutoff')
      const r = range.getBoundingClientRect()
      const fill = q('.range-fill').getBoundingClientRect()
      const ticks = [...document.querySelectorAll('.ticks span')]
      const i = Number(range.value)
      return {
        value: range.value,
        chip: q('#vintage-chip').textContent,
        fillW: Math.round(fill.width * 10) / 10,
        expectedFill: Math.round((i / 7) * (r.width - 28) * 10) / 10,
        tickCenter: Math.round(ticks[i].getBoundingClientRect().left + ticks[i].getBoundingClientRect().width / 2 - r.left),
        thumbCenter: Math.round(14 + (i / 7) * (r.width - 28)),
      }
    })

  const setIndex = async (i) => {
    await page.evaluate((idx) => {
      const range = document.querySelector('#cutoff')
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set
      setter.call(range, String(idx))
      range.dispatchEvent(new Event('input', { bubbles: true }))
    }, i)
    await page.waitForFunction((idx) => document.querySelector('#cutoff').value === String(idx), i)
    await page.waitForTimeout(100)
    return measure()
  }

  const all = []
  for (let i = 0; i <= 7; i++) all.push(await setIndex(i))

  await setIndex(3)
  await page.locator('#charts').scrollIntoViewIfNeeded()
  await page.waitForTimeout(400)
  const geom = await page.evaluate(() => {
    const r = document.querySelector('#cutoff').getBoundingClientRect()
    return { left: r.left, width: r.width, top: r.top, height: r.height }
  })
  const y = geom.top + geom.height / 2
  const xFor = (i) => geom.left + 14 + (i / 7) * (geom.width - 28)
  await page.mouse.move(xFor(3), y)
  await page.mouse.down()
  await page.mouse.move(xFor(6), y, { steps: 14 })
  await page.mouse.up()
  await page.waitForTimeout(350)
  const dragged = await measure()

  const shots = []
  for (const theme of ['light', 'dark']) {
    await page.evaluate((t) => {
      document.documentElement.dataset.theme = t
      localStorage.setItem('ww-theme', t)
    }, theme)
    await page.waitForTimeout(400)
    await page.locator('#charts').scrollIntoViewIfNeeded()
    await page.waitForTimeout(400)
    const path = `${OUT}/chrome-${theme}.png`
    await page.screenshot({ path })
    shots.push(path)
  }

  await browser.close()
  return { errors, all, dragged, shots }
}

main()
  .then((r) => console.log(JSON.stringify(r, null, 2)))
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
