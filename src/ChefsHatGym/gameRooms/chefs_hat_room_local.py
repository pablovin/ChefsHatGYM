from datetime import datetime
import os
import time
from ChefsHatGym.env import ChefsHatEnv
from ChefsHatGym.agents.chefs_hat_agent import ChefsHatAgent
import gym
import numpy as np

import ChefsHatGym.utils.utils as utils

class ChefsHatRoomLocal:

    def get_room_id(self):
        return self.room_id
    
    def get_log_directory(self):
        return self.log_directory
    
    def get_number_players(self):
        return len(self.players_names)
    
    def get_room_finished(self):
        return self.room_finished
    
    def __init__( 
        self, room_name: str,  
        game_type : str = ChefsHatEnv.GAMETYPE["MATCHES"],        
        stop_criteria : int = 10,
        max_rounds : int = -1,
        verbose : bool = True,        
        save_dataset : bool = True,                
        save_game_log : bool = True,    
        log_directory : str =None,       
        timeout_player_response : int = 5,
    ) -> None:
        
        #game type parameters
        self.room_name = room_name
        self.game_type = game_type
        self.stop_criteria = stop_criteria
        self.max_rounds = max_rounds
        self.verbose = verbose
        self.save_dataset = save_dataset        
        self.save_game_log = save_game_log
        
        self.timeout_player_response = timeout_player_response        

        #In-game parameters        
        self.players = []
        self.players_names = []
        self.receive_messages_subs = {}
        self.room_finished = False
        self.ready_to_start = False

        #Create the log directory
        if not log_directory:
            log_directory = "temp/"

        self.log_directory = os.path.join(log_directory, f"{datetime.now().strftime("%H-%M%S")}_{room_name}")
        os.makedirs(self.log_directory)
        
        #Creating logger
        self.logger = utils.logging.getLogger("ROOM")                            
        self.logger.addHandler(utils.logging.FileHandler(os.path.join(self.log_directory, "rom_log.log"), mode='w', encoding='utf-8'))        

        self.log("---------------------------")
        self.log("Creating logger")  
        self.log(f"[Room]:  - folder: { self.log_directory}")  

            
        #Create a room
        self.room_id = room_name          

    def log(self, message):
        if self.verbose:
            self.logger.info(f"[Room]: {message}")

    def error(self, message):
        if self.verbose:
            self.logger.critical(f"[Room]: {message}")


    def add_player(self, player:ChefsHatAgent):        
        
        if len(self.players) <4:            
            
            if player.get_name() in self.players_names:
                self.error(f"[Room][ERROR]: Player names must be unique! Trying to add {[player.get_name()]} to existing players: {self.players_names}!")                 
                raise Exception("Players with the same name!")
            
            self.players.append(player)
            self.players_names.append(player.get_name())
            self.log(f"[Room]:  - Player {player.get_name()} connected! Current players: {self.players_names}")
        else:                
                self.error(f"[Room][ERROR]: Room is full!! Player not added! Current players: {self.players_names}!")          
            
                    
    def start_new_game(self, game_verbose=False):      

        if len(self.players) <4:            
            self.error(f"[Room][ERROR]: Not enough players to start the game! Total current players: {len(self.players_names)}")  
        else:
            
            self.log("---------------------------")
            self.log("Initializing a game")        
                        
            """Setup environment"""
            self.env = gym.make('chefshat-v1') #starting the game Environment
            self.env.startExperiment(           
                gameType = self.game_type,
                stopCriteria = self.stop_criteria,
                maxRounds = self.max_rounds,
                playerNames = self.players_names,
                logDirectory = self.log_directory,
                verbose = game_verbose,
                saveDataset = self.save_dataset,
                saveLog = self.save_game_log
            )

            self.log(" - Environment initialized!")
            observations = self.env.reset()
                            
            while not self.env.gameFinished:

                currentPlayer = self.players[self.env.currentPlayer]
                self.log(f"[Room]:  -- Round {self.env.rounds} -  Current player: {currentPlayer.get_name()}")  
                observations = self.env.getObservation()

                info = {"validAction":False}
                while not info["validAction"]:
                    timeNow = datetime.now()                    
                    action = currentPlayer.getAction(observations)

                    self.log(f"[Room]:  ---- Round {self.env.rounds} Action: {np.argmax(action)}")
                    nextobs, reward, isMatchOver, truncated, info = self.env.step(action)            
                
                    if not info["validAction"]:
                        self.error(f"[Room][ERROR]: ---- Invalid action!")      

                #Send action update to the current agent
                currentPlayer.actionUpdate(info)                

                # Observe others
                for p in self.players:
                    if p != currentPlayer:
                        p.observeOthers(info)

                #Match is over
                if isMatchOver:
                    self.log(f"[Room]:  -- Match over! Total rounds: {self.env.rounds}")                        

                    #Players are updated that the match is over
                    for p in self.players:
                        p.matchUpdate(info)

                    #A new match is started, with the cards at hand being reshuffled
                    # Check if any player is capable of doing a special action
                    # Sinalize the player that he can do a special action, wait for reply

                    if not self.env.gameFinished:
                        players_actions = self.env.list_players_with_special_actions()  
                        doSpecialAction = False
                        playerSpecialAction = -1                  
                        if len(players_actions)>1:
                            for player_action in players_actions:
                                player = player_action[0]
                                action = player_action[1]
                                doSpecialAction = self.playersp[player].doSpecialAction(info, action)
                                if doSpecialAction:
                                    self.env.doSpecialAction(player, action)                                
                                    playerSpecialAction = player
                                    break
                                            
                        #Once the cards are handled again, the chef and sous-chef have to choose which cards to give
                        player_sourchef, sc_cards, player_chef, chef_cards = self.env.get_chef_souschef_roles_cards()

                        souschefCard = self.players[player_sourchef].exchangeCards(sc_cards, 1)
                        chefCards = self.players[player_chef].exchangeCards(chef_cards, 2)
                        self.env.exchange_cards(souschefCard, chefCards, doSpecialAction, playerSpecialAction)

                    
            #Game over!
            self.room_finished = True   
            return info
    
            


        
