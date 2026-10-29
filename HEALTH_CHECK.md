# Health Check Configuration

## Render Native Health Check

The `/health` endpoint has been added/verified. To configure Render's native HTTP health check:

### Using render.yaml (Blueprint) - Already configured
The `render.yaml` now includes `healthCheckPath: /health`. If you deploy using Render Blueprints, this will be applied automatically.

### Using Render Dashboard (Manual)
1. Go to your service in the [Render Dashboard](https://dashboard.render.com/)
2. Go to **Settings** → **Health Check**
3. Set **Health Check Path** to `/health`
4. Render will periodically check this endpoint. If it returns non-2xx, Render may restart the instance.
5. Save changes

**Note:** On Render's free tier, services sleep after inactivity. Render's native health checks do **not** prevent free-tier sleep - they only restart unhealthy instances while the service is running.

## External Uptime Monitoring (Every 5 Minutes)

Since Render's free tier sleeps after inactivity and native health checks won't prevent sleep, you can use an external uptime monitor to ping your service periodically:

### Recommended Services
- [UptimeRobot](https://uptimerobot.com/) - Free tier allows 5-minute intervals
- [Better Stack](https://betterstack.com/) - Free tier available
- [Pingdom](https://www.pingdom.com/) - Has free options
- [Healthchecks.io](https://healthchecks.io/) - Free for basic use

### Setup Instructions (UptimeRobot example)
1. Create an account at [uptimerobot.com](https://uptimerobot.com/)
2. Click **Add New Monitor**
3. Set **Monitor Type** to `HTTP(s)`
4. Set **Friendly Name** to `Windward API Health`
5. Set **URL (or IP)** to `https://your-backend-url.onrender.com/health`
6. Set **Monitoring Interval** to `5 minutes`
7. Configure **Alert Contacts** (email, SMS, etc.) to notify you if it goes down
8. Click **Create Monitor**

### Setup Instructions (Better Stack example)
1. Create an account at [betterstack.com](https://betterstack.com/)
2. Go to **Uptime** → **Create monitor**
3. Set URL to `https://your-backend-url.onrender.com/health`
4. Set check frequency to `5 minutes`
5. Configure notifications for downtime
6. Save

**Important:** These external pings will help keep the service awake on some free tiers, but behavior depends on the hosting provider's sleep policies. There is no way for the application itself to wake a sleeping service via internal timers or self-pinging loops.
