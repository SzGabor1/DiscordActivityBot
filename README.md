# DiscordActivityBot

A Discord bot that tracks user activity on your server and provides insightful statistics.

## Features

- Track the total time users have spent on the server.
- Check the current uptime of users online.
- Generate Gantt charts for user activity on specific days.

## Setup

### Requirements

1. **Webhook**: You need to set up a webhook in a channel named `activity_watch` on your server.
2. **MongoDB**: The bot uses MongoDB as its database.
3. **Environment Variables**: Make sure to configure the required environment variables.

### Environment Variables

| Variable Name      | Description                            |
|--------------------|----------------------------------------|
| `DISCORD_TOKEN`    | Your Discord bot token.               |
| `MONGO_URI`        | MongoDB connection string.            |
| `WEBHOOK_URL`      | URL of the `activity_watch` webhook.  |

### Commands

| Command   | Description                                                                                  |
|-----------|----------------------------------------------------------------------------------------------|
| `!alltime`| Displays the total time spent on the server by all users who have ever joined.               |
| `!uptime` | Shows how long the currently online users have been active.                                  |
| `!gant`   | Generates a Gantt chart for the current day's user activity.                                 |

### Invite Link

Once your bot is set up, replace the placeholder below with the generated invite link to allow others to add your bot to their servers.

**Invite Link**: [Click Here](https://discord.com/oauth2/authorize?client_id=1306298464870731806&permissions=412317239296&integration_type=0&scope=bot)

## Usage

1. Ensure the `activity_watch` channel is created and the webhook is correctly set up.
2. Add the bot to your server using the invite link.
3. Start interacting with the bot using the available commands.

Enjoy tracking user activity with DiscordActivityBot!
