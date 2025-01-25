import os
import json
import openai

class TextAdventureGame:
    def __init__(self, game_data_path):
        with open(game_data_path, 'r') as f:
            self.game_data = json.load(f)

        self.rooms = self.game_data.get("rooms", {})
        self.npcs = self.game_data.get("npcs", {})
        self.player_data = self.game_data.get("player", {})
        self.current_room = self.player_data.get("start_room", "")
        self.inventory = self.player_data.get("inventory", [])

        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_room_description(self, room):
        # prompt = (
        #     "You are a game narrative engine. Given a meta description, produce a vivid, immersive, "
        #     "and thematically consistent room description for players. Keep it to 2-3 sentences. "
        #     f"Meta description: {room['meta_description']}"
        # )


        system_prompt = "You are a game narrative engine. Given a meta description, produce a vivid, immersive, "
        "and thematically consistent room description for players."
        user_prompt = f"Meta description: {room['meta_description']}. Please keep the room description to 2-3 sentences."
        
        prompt =  [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
            
            ]

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=prompt,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print("Error calling OpenAI API:", e)
            return room['meta_description']

    def generate_npc_dialogue(self, npc_id, player_input=None):
        npc_data = self.npcs.get(npc_id, {})
        # prompt = (
        #     f"You are a character in a text adventure game. Your personality: {npc_data['meta_description']}. "
        #     "The player has asked you something or approached you. Please respond in one or two sentences. "
        # )

        system_prompt = f"You are a character in a text adventure game. Your personality: {npc_data['meta_description']}."
        user_prompt = "The player has asked you something or approached you. Please respond in one or two sentences."

        if player_input:
            user_prompt += f"\nPlayer input: {player_input}\n"
        
        prompt =  [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
            
            ]

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=prompt,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print("Error calling OpenAI API:", e)
            return "The NPC stares silently, unable to respond."

    def describe_current_room(self):
        room = self.rooms[self.current_room]
        description = self.generate_room_description(room)
        print(f"\n{room['name']}")
        print(description)
        # Check if there's an NPC
        npc_id = room.get("npc", None)
        if npc_id:
            dialogue = self.generate_npc_dialogue(npc_id)
            npc_name = self.npcs[npc_id]['name']
            print(f"\n{npc_name} says: \"{dialogue}\"")

    def get_user_input(self):
        return input("\n> ").strip().lower()

    def move_player(self, direction):
        room = self.rooms[self.current_room]
        exits = room.get("exits", {})
        if direction in exits:
            self.current_room = exits[direction]
            print(f"You move {direction} to the {self.rooms[self.current_room]['name']}.")
        else:
            print("You can't go that way.")

    def talk_to_npc(self):
        room = self.rooms[self.current_room]
        npc_id = room.get("npc", None)
        if npc_id:
            player_input = input("What do you say? ")
            response = self.generate_npc_dialogue(npc_id, player_input)
            print(f"{self.npcs[npc_id]['name']} replies: \"{response}\"")
        else:
            print("There's no one here to talk to.")

    def play(self):
        print("Welcome to the Text Adventure!")
        self.describe_current_room()

        while True:
            command = self.get_user_input()

            if command in ["quit", "exit"]:
                print("Thanks for playing!")
                break
            elif command in ["north", "south", "east", "west"]:
                self.move_player(command)
                self.describe_current_room()
            elif command.startswith("talk"):
                self.talk_to_npc()
            elif command in ["look", "examine"]:
                self.describe_current_room()
            else:
                print("I don't understand that command.")

if __name__ == "__main__":
    game = TextAdventureGame("game_data.json")
    game.play()