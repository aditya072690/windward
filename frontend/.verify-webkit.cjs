const { webkit } = require('playwright')

const URL = 'http://localhost:5175/'
const OUT = '/private/var/folders/cc/v6dtqkmd4bg3721nfmp509_c0000gn/T/opencode'

async function main() {
  const browser = await webkit.launch()
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } })
  const errors = []
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text())
  })
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message))

  await page.goto(URL, { waitUntil: 'networkidle' })
  await page.waitForSelector('#day')
  await page.waitForFunction(() => document.querySelectorAll('.ticks span').length === 8)

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
        disabled: range.disabled,
        fillW: Math.round(fill.width * 10) / 10,
        expectedFill: Math.round((i / 7) * (r.width - 28) * 10) / 10,
        tickCenter: Math.round(ticks[i].getBoundingClientRect().left + ticks[i].getBoundingClientRect().width / 2 - r.left),
        thumbCenter: Math.round(14 + (i / 7) * (r.width - 28)),
        help: q('#cutoff-help').textContent.replace(/\s+/g, ' ').trim(),
        day: { value: q('#day').value, min: q('#day').min, max: q('#day').max },
        title: q('#main-card-title').textContent,
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
    await page.waitForTimeout(120)
    return measure()
  }

  const all = []
  for (let i = 0; i <= 7; i++) all.push(await setIndex(i))

  // Real pointer drag from the current thumb (index 3) toward index 5.
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
  await page.mouse.move(xFor(5), y, { steps: 12 })
  await page.mouse.up()
  await page.waitForTimeout(350)
  const dragged = await measure()

  // Day control.
  await page.evaluate(() => {
    const day = document.querySelector('#day')
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set
    setter.call(day, '2026-01-20')
    day.dispatchEvent(new Event('input', { bubbles: true }))
    day.dispatchEvent(new Event('change', { bubbles: true }))
  })
  await page.waitForFunction(() => document.querySelector('#main-card-title').textContent.includes('20 January'))
  await page.waitForTimeout(250)
  const dayChanged = await measure()

  // Latest mode.
  await page.getByRole('radio', { name: 'Latest' }).click()
  await page.waitForFunction(() => document.querySelector('#cutoff').disabled)
  await page.waitForTimeout(350)
  const latest = await page.evaluate(() => {
    const cutoff = document.querySelector('.cutoff')
    return {
      disabled: document.querySelector('#cutoff').disabled,
      opacity: getComputedStyle(cutoff).opacity,
      fillColor: getComputedStyle(document.querySelector('.range-fill')).backgroundColor,
      help: document.querySelector('#cutoff-help').textContent.replace(/\s+/g, ' ').trim(),
      ledgerRows: [...document.querySelectorAll('#vintage-body tr')].map((tr) =>
        tr.textContent.replace(/\s+/g, ' ').trim().slice(0, 60),
      ),
    }
  })

  // Screenshots, light and dark, scrolled to the controls.
  for (const theme of ['light', 'dark']) {
    await page.evaluate((t) => {
      document.documentElement.dataset.theme = t
      localStorage.setItem('ww-theme', t)
    }, theme)
    await page.getByRole('radio', { name: 'Decision-time' }).click()
    await page.waitForTimeout(300)
    await page.locator('#charts').scrollIntoViewIfNeeded()
    await page.waitForTimeout(500)
    await page.screenshot({ path: `${OUT}/webkit-${theme}.png` })
  }

  await browser.close()
  return { errors, all, dragged, dayChanged, latest }
}

main()
  .then((r) => {
    console.log(JSON.stringify(r, null, 2))
  })
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
