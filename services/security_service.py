class SecurityService:
    @staticmethod
    def check_link(content: str) -> bool:
        forbidden = ["http://", "https://", "discord.gg/"]
        return any(f in content for f in forbidden)
      
