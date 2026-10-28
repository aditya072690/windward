const pw = require('playwright')

const URL = 'http://localhost:5175/'

async function run(kind) {
  const browser =
    kind === 'webkit'
      ? await pw.webkit.launch()
      : await pw.chromium.launch({ channel: 'chrome' })
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } })
  await page.goto(URL, { waitUntil: 'networkidle' })
  await page.waitForSelector('#day')
  await page.waitForTimeout(500)

  const segCheck = async () => {
    const r = await page.evaluate(() => {
      const thumb = document.querySelector('.seg-thumb').getBoundingClientRect()
      const active = document.querySelector('.segmented button[aria-checked="true"]').getBoundingClientRect()
      return {
        thumb: { left: Math.round(thumb.left), width: Math.round(thumb.width) },
        active: { left: Math.round(active.left), width: Math.round(active.width) },
        deltaLeft: Math.round(thumb.left - active.left),
        deltaWidth: Math.round(thumb.width - active.width),
      }
    })
    return r
  }

  const segDecision = await segCheck()
  await page.getByRole('radio', { name: 'Latest' }).click()
  await page.waitForTimeout(400)
  const segLatest = await segCheck()
  await page.getByRole('radio', { name: 'Decision-time' }).click()
  await page.waitForTimeout(300)

  // Keyboard control.
  await page.locator('#cutoff').focus()
  await page.keyboard.press('ArrowRight')
  await page.waitForTimeout(150)
  const keyboard = await page.evaluate(() => ({
    value: document.querySelector('#cutoff').value,
    chip: document.querySelector('#vintage-chip').textContent,
  }))

  const counts = await page.evaluate(() => ({
    svgs: document.querySelectorAll('.chart-shell svg').length,
    ledgerRows: document.querySelectorAll('#vintage-body tr').length,
    dayValue: document.querySelector('#day').value,
  }))

  // Narrow layout overflow check.
  await page.setViewportSize({ width: 390, height: 844 })
  await page.waitForTimeout(500)
  const narrow = await page.evaluate(() => {
    const card = document.querySelector('.card.controls')
    const range = document.querySelector('#cutoff').getBoundingClientRect()
    const ticks = [...document.querySelectorAll('.ticks span')]
    return {
      cardOverflow: card.scrollWidth - card.clientWidth,
      docOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      rangeWidth: Math.round(range.width),
      firstTick: Math.round(ticks[0].getBoundingClientRect().left - range.left),
      lastTick: Math.round(ticks[7].getBoundingClientRect().left + ticks[7].getBoundingClientRect().width - range.right),
      dayWidth: Math.round(document.querySelector('#day').getBoundingClientRect().width),
    }
  })

  await browser.close()
  return { kind, segDecision, segLatest, keyboard, counts, narrow }
}

;(async () => {
  const out = []
  for (const kind of ['webkit', 'chrome']) {
    try {
      out.push(await run(kind))
    } catch (e) {
      out.push({ kind, error: String(e) })
    }
  }
  console.log(JSON.stringify(out, null, 2))
})()
