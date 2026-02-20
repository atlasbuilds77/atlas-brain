module.exports = {
  apps: [
    {
      name: "titan-v3",
      script: "python3",
      args: "titan_main.py",
      cwd: "/Users/atlasbuilds/clawd/titan-trader",
      cron_restart: "0 4 * * 1-5",  // 4:00 AM ET Mon-Fri (adjust for your TZ)
      autorestart: false,            // One session per day
      max_restarts: 1,
      env: {
        PYTHONUNBUFFERED: "1",
        TZ: "America/New_York",
        // Set these or use credentials.json
        // TITAN_TG_TOKEN: "your-bot-token",
        // TITAN_TG_CHAT: "your-chat-id",
      },
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      error_file: "/Users/atlasbuilds/clawd/titan-trader/logs/pm2-error.log",
      out_file: "/Users/atlasbuilds/clawd/titan-trader/logs/pm2-out.log",
    },
  ],
};
