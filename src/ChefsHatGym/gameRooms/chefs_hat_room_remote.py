import redis

from datetime import datetime
import os
import time
from ChefsHatGym.env import ChefsHatEnv
import gym
import json
import numpy as np

import ChefsHatGym.utils.utils as utils

REQUEST_TYPE ={"requestAction" : "GetAction", "sendAction" : 1, "actionUpdate":"UpdateAgent", "updateOthers":"ObserveOthers", "matchOver":"MatchOver", "gameOver":"GameOver", "doSpecialAction":"DoSpecialAction", "exchangeCards":"ExchangeCards"}

class ChefsHatRoomRemote:

    def get_room_id(self):
        return self.room_id
    
    def get_log_directory(self):
        return self.log_directory
    
    def get_number_players(self):
        return len(self.players_names)
    
    def get_room_finished(self):
        return self.room_finished
    
    def __init__( 
        self, room_name: str, redis_url: str = "localhost", redis_port: str = "6379", 
        game_type : str = ChefsHatEnv.GAMETYPE["MATCHES"],        
        stop_criteria : int = 10,
        max_rounds : int = -1,
        verbose : bool = True,
        save_dataset : bool = True,                
        save_game_log : bool = True,    
        log_directory : str =None,
        timeout_player_subscribers : int = 30,
        timeout_player_response : int = 5,
    ) -> None:
        
        #Redis parameters
        self.redis_url = redis_url
        self.redis_port = redis_port

        #game type parameters
        self.room_name = room_name
        self.game_type = game_type
        self.stop_criteria = stop_criteria
        self.max_rounds = max_rounds
        self.verbose = verbose
        self.save_dataset = save_dataset        
        self.save_game_log = save_game_log

        self.timeout_player_subscribers = timeout_player_subscribers
        self.timeout_player_response = timeout_player_response        

        #In-game parameters
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

        self.log("[Room]: ---------------------------")
        self.log("[Room]: Creating logger")  
        self.log(f"[Room]:  - folder: { self.log_directory}")  

        #Connect to Redis
        self._connect_to_redis()                

        #Create a room
        self._create_room()                 

        #Wait players to connect
        self._prepare_connect_player()


    def log(self, message):
        if self.verbose:
            self.logger.info(f"[Room]: {message}")

    def error(self, message):
        if self.verbose:
            self.logger.critical(f"[Room]: {message}")



    def _connect_to_redis(self):
        self.log("[Room]: ---------------------------")
        self.log("[Room]: Connecting with Redis")        

        self.log(f"[Room]:  - Connecting to Redis Server: {self.redis_url}:{self.redis_port}")

        try:
            self.redis_server = redis.Redis(
                self.redis_url, self.redis_port, charset="utf_8", decode_responses=True
            )                      

            time.sleep(3)  
            self.log(f"[Room]:  - Connected with succcess!")
        except:            
            self.error(f"[Room][ERROR]: Connection failed! Please check the URL/Port")
            raise redis.exceptions.ConnectionError          

        self.log("[Room]: --------------     -------------")                  

    def _create_room(self):
        
        self.log("[Room]: ---------------------------")
        self.log("[Room]: Creating a room")        

        self.room_id = self.room_name

        available_channels = self.redis_server.pubsub_channels()

        if self.room_id in available_channels:
            self.error(f"[Room][ERROR]: Room already exists!")       
            raise Exception("Room exists!!") 
        
        self.log(f"[Room]:  - Room created with sucess: {self.room_id}!")

        self.log("[Room]: --------------     -------------")

        self.redis_server.set(self.room_id, self.log_directory)
        
    def _prepare_connect_player(self):
        self.log("[Room]: ---------------------------")
        self.log("[Room]: Connecting players")                

        self.room_subscriber = self.redis_server.pubsub(ignore_subscribe_messages =True)         
        self.room_subscriber.subscribe(**{f"{self.room_id}subscribe":self.add_player})                 
                   
        self._wait_for_players()   

    @utils.threaded
    def _wait_for_players(self):
        self.log("[Room]: - Waiting for players to connect...")        
        timenow = datetime.now()
        while (len(self.players_names) <4):
            self.room_subscriber.get_message()
            time.sleep(0.001)
            elapsedTime = (datetime.now() - timenow).total_seconds()
            # print (f"Elapsed time: {elapsedTime}")
            if elapsedTime > self.timeout_player_subscribers:
                self.error(f"[Room][ERROR]: Players subscription timeout! Current playes: {self.players_names}")                 
                raise Exception("Player subscription timeout!")                
            pass

        self.ready_to_start = True


    def add_player(self, message:str):        
        data = json.loads(message["data"])
        playerName = data["playerName"]

        if playerName in self.players_names:
            self.error(f"[Room][ERROR]: Player names must be unique! Trying to add {[playerName]} to existing players: {self.players_names}!")                 

        else:
            if len(self.players_names) > 4:                
                self.error(f"[Room][ERROR]: Room is full!! Player not added! Current players: {self.players_names}!")          
            else:
                self.players_names.append(playerName)

                # receive_messages_subs
                thisSubscriber = self.redis_server.pubsub(ignore_subscribe_messages =True) 


                thisSubscriber.subscribe(f"{self.room_id}{playerName}Agent")
                self.receive_messages_subs[playerName] = thisSubscriber

                self.log(f"[Room]:  - Player {playerName} connected! Current players: {self.players_names}")


    def _send_message_agent(self,info, playerName, actionType, expectReturn):        
                
        info["type"] = actionType
        self.redis_server.publish(f"{self.room_id}{playerName}Server", json.dumps(info))        
        self.log(f"[Room]:  ---- {actionType} request to the agent")  

        if expectReturn:
            timenow = datetime.now()
            while True:                              
                message = self.receive_messages_subs[playerName].get_message()

                if message:
                    actionMessage = json.loads(message["data"])
                    action = actionMessage["agent_action"]
                    self.log(f"[Room]:  ---- Message received: {action}!")                    
                    break
                else:
                    time.sleep(1)
                    timeElapsed = (datetime.now() - timenow).total_seconds()
                    if timeElapsed > self.timeout_player_response:

                        if actionType == REQUEST_TYPE["requestAction"]:
                            action = np.zeros(200)
                            action[-1] = 1
                        elif actionType == REQUEST_TYPE["doSpecialAction"]:
                            action = False
                        elif actionType == REQUEST_TYPE["exchangeCards"]:
                             cards = info["cards"]
                             amount = info["amount"]
                             action = sorted(cards[-amount:])

                        self.error(f"[Room][ERROR]: ---- Response timeout! Default action chose: {action}.")        
                        break

            return action
    


    @utils.threaded
    def start_new_game(self, game_verbose=False):      

        while not self.ready_to_start:
            time.sleep(5)
            self.error(f"[Room][ERROR]: Not enough players to start the game! Total current players: {len(self.players_names)}")  

        self.log("[Room]: ---------------------------")
        self.log("[Room]: Initializing a game")        
                    
        """Setup environment"""
        self.env = gym.make('chefshat-v1') #starting the game Environment
        self.env.startExperiment(           
            gameType = self.game_type,
            stopCriteria = self.stop_criteria,
            maxRounds= self.max_rounds,
            playerNames = self.players_names,
            logDirectory = self.log_directory,
            verbose = game_verbose,
            saveDataset = self.save_dataset,
            saveLog = self.save_game_log
        )

        self.log("[Room]:  - Environment initialized!")

        observations = self.env.reset()
                        
        while not self.env.gameFinished:

            currentPlayer = self.players_names[self.env.currentPlayer]
            self.log(f"[Room]:  -- Current player: {currentPlayer}")  
            observations = self.env.getObservation()

            info = {"validAction":False}
            while not info["validAction"]:

                info["observations"] = observations.tolist()
                action = self._send_message_agent(info, currentPlayer, REQUEST_TYPE["requestAction"], True)

                # action = self._request_action(currentPlayer, observations)
                self.log(f"[Room]:  ---- Action: {np.argmax(action)}")
                nextobs, reward, isMatchOver, truncated, info = self.env.step(action)            
            
                if not info["validAction"]:
                    self.error(f"[Room][ERROR]: ---- Invalid action!")      

            #Send action update to the current agent
            # self._send_action_update(currentPlayer, info)
            self._send_message_agent(info, currentPlayer, REQUEST_TYPE["actionUpdate"], False)


            # Observe others
            for p in self.players_names:
                if p != currentPlayer:
                    # self._send_update_others(p, info)
                    self._send_message_agent(info, p, REQUEST_TYPE["updateOthers"], False)

            #Match is over
            if isMatchOver:
                self.log(f"[Room]:  -- Match over!")       
                for p in self.players_names:
                    # self._send_match_over(p, info)      
                    self._send_message_agent(info, p, REQUEST_TYPE["matchOver"], False)



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
                            
                            info_special = {}
                            info_special["special_action"] = action
                            action = self._send_message_agent(info_special, self.players_names[player], REQUEST_TYPE["doSpecialAction"], True)

                            # doSpecialAction = self._request_special_action(self.players_names[player], info, action)                            
                            if doSpecialAction:
                                self.env.doSpecialAction(player, action)                                
                                playerSpecialAction = player
                                break
                                        
                    #Once the cards are handled again, the chef and sous-chef have to choose which cards to give
                    player_sourchef, sc_cards, player_chef, chef_cards = self.env.get_chef_souschef_roles_cards()

                    info_special = {}                    
                    info_special["cards"] = sc_cards
                    info_special["amount"] = 1
                    souschefCard = self._send_message_agent(info_special, self.players_names[player_sourchef], REQUEST_TYPE["exchangeCards"], True)
            
                    info_special = {}                    
                    info_special["cards"] = chef_cards
                    info_special["amount"] = 2
                    chefCards = self._send_message_agent(info_special, self.players_names[player_chef], REQUEST_TYPE["exchangeCards"], True)

                    # souschefCard = self.players[player_sourchef].exchangeCards(sc_cards, 1)
                    # chefCards = self.players[player_chef].exchangeCards(chef_cards, 2)


                    self.env.exchange_cards(souschefCard, chefCards, doSpecialAction, playerSpecialAction)                  


        #Game over!
        self.room_finished = True   

        print(f"Performance score: {info['performanceScore']}")
        print(f"Scores: {info['score']}")

        for p in self.players_names:
            # self._send_game_over(p)  
            info={}            
            self._send_message_agent(info, p, REQUEST_TYPE["gameOver"], False)   
          


        
