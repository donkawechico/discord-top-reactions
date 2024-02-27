# Top Reactions Discord Bot Installation Guide

This guide will walk you through the process of installing and setting up the Top Reactions Discord Bot on a Windows environment. The bot is containerized using Docker, ensuring a smooth and consistent setup process across different systems.


## Step 1: Install Docker Desktop on Windows

1. **Download Docker Desktop for Windows**: Visit the [official Docker website](https://www.docker.com/products/docker-desktop) and download the Docker Desktop installer for Windows.
2. **Install Docker Desktop**: Run the installer and follow the on-screen instructions. Ensure the "Enable Hyper-V Windows Features" option is selected to allow Docker to manage it.
3. **Restart Your Computer**: A restart is necessary to complete the Hyper-V installation.
4. **Start Docker Desktop**: After restarting, launch Docker Desktop from the Start menu. Initial startup may take a few minutes.

## Step 2: Configure Docker to Start Automatically

1. **Open Docker Desktop Settings**: Right-click the Docker icon in the system tray and select "Settings".
2. **General Settings**: Ensure the "Start Docker Desktop when you log in" option is checked. This ensures Docker runs automatically at system startup.

## Step 3: Download the Bot Project

1. **Clone or Download the Project**: Download the project from its GitHub repository.
   ```bash
   git clone https://github.com/donkawechico/discord-top-reactions.git
   cd discord-top-reactions
2. **Environment Configuration**: Copy the `.env.example` file to a new file named `.env` and fill in your Discord bot token and any other required variables.

## Step 4: Build and Run the Bot Using Docker

1. **Open PowerShell or Command Prompt**: Navigate to the project directory.
2. **Build the Docker Image**: Run the following command to build your Docker image:
    ```bash
    docker build -t top-reactions-bot .
    ```
3. **Run the Bot Container**: Use the following command to run your bot:
   ```bash
   docker run --env-file .env --restart unless-stopped top-reactions-bot
   ```
   The `--restart unless-stopped` option ensures that the Docker container will automatically restart if it crashes or if the server is rebooted.

## Step 5: Verify Bot is Running

- After running the Docker container, you should see your bot coming online in your Discord server.
- To verify the bot is set to auto-start, you can reboot your machine and check if the bot comes online automatically.

## Troubleshooting

If you encounter any issues during the installation or operation of your bot, refer to the Docker Desktop and Discord bot documentation for troubleshooting tips. You can also check the logs of your Docker container for any error messages:

```bash
docker logs <container_id>
```

Replace `<container_id>` with the ID of your bot's Docker container. You can find the container ID by running `docker ps`.

## Support

For additional help or questions, please open an issue on the GitHub repository page.

