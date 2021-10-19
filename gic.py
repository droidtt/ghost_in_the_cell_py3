import sys
import math

"""
#Entity - super class

id: entity_id
owner: player that owns the factory: 1 for you, -1 for your opponent and 0 if neutral
"""
class Entity():
    def __init__(self, id, owner):
        self.id = id
        self.owner = owner


"""
#FACTORY - Entity sub-class

cyborgs: number of cyborgs in the factory
production: factory production (between 0 and 3)
producing_again: number of turns before the factory starts producing again (0 means that the factory produces normally)
"""
class Factory(Entity):
    def __init__(self,id,owner,cyborgs,production,producing_again):
        super().__init__(id,owner)
        self.cyborgs = cyborgs
        self.production = production
        self.producing_again = producing_again
    

        

"""
#TROOP - Entity sub-class

source: identifier of the factory from where the troop leaves
dest: identifier of the factory targeted by the troop
cyborgs: number of cyborgs in the troop (positive integer)
remaining_turns: remaining number of turns before the troop arrives (positive integer)
"""

class Troop(Entity):
    def __init__(self,id,owner,source,dest,cyborgs,remaining_turns):
        super().__init__(id,owner)
        self.source = source
        self.dest = dest
        self.cyborgs = cyborgs
        self.remaining_turns = remaining_turns

"""
#BOMB - Entity sub-class

source: identifier of the factory from where the bomb is launched
dest: identifier of the targeted factory if it's your bomb, -1 otherwise
remaining_turns: remaining number of turns before the bomb explodes (positive integer) if that's your bomb, -1 otherwise
"""

class Bomb(Entity):
    def __init__(self,id,owner,source,dest,remaining_turns):
        super().__init__(id,owner)
        self.source =source
        self.dest = dest
        self.remaining_turns = remaining_turns

"""
#IndirectedGraph

indirected graph with weights implementaion

adjacency_dict - dictionary that holds connectivity between nodes (factories)
weights_dict- dictionary that hold weights (distance) between nodes (factories)

ref : https://stackoverflow.com/questions/58157354/python-create-a-graph-from-a-dictionary
"""

class IndirectedGraph:
    def __init__(self):
        self.adjacency_dict = {}
        self.weights_dict = {}

    #add to dict 2 directions between two nodes
    def add_weight(self, node_1, node_2, distance):
        key_weight = '%s_%s' % (node_1, node_2)
        self.weights_dict[key_weight] = distance
        key_weight = '%s_%s' % (node_2, node_1)
        self.weights_dict[key_weight] = distance

    #get weight by the key between nodes
    def get_weight(self, node_1, node_2):
        key_weight = '%s_%s' % (node_1, node_2)
        return self.weights_dict[key_weight]

    #add adjacency between nodes
    def add_connection(self, source, dest, weight):
        self.add_weight(source, dest, weight)

        if source in self.adjacency_dict:
            self.adjacency_dict[source].append(dest)
        else:
            self.adjacency_dict[source] = [dest]

        if dest in self.adjacency_dict:
            self.adjacency_dict[dest].append(source)
        else:
            self.adjacency_dict[dest] = [source]


"""
#CentralRepository

data collected
"""

class CentralRepository:
    def __init__(self):
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)

    def get_entities(self):
        return self.entities
"""
#Bot

the kernel's program, consist of modes, decisions and queries
"""
class Bot:
    modes = ['WAIT','ATTACK','DEFENCE','STRENGTH']
    current_mode = modes[0]
    command = ''
    MAX_TURNS_FOR_TROOP,MAX_RANGE_FACTORY  = 20,20
    
    def __init__(self, entities):
        self.entities = entities
        print("LOG: entities leng %s"%len(self.entities), file=sys.stderr)
        self.command = ''

    def append_command(self, command):
        if self.command == '':
            self.command = command
        elif len(self.command) > 3:
            self.command += ';'
            self.command += command

    #updates mode each turn
    def set_bot_mode(self):
        self.current_mode = 'WAIT'
        print("LOG: set_bot_mode", file=sys.stderr)
        all_my_cyborgs,all_other_cyborgs = self.get_cyborgs()
        print("LOG: all_my_cyborgs[0] %s" % all_my_cyborgs, file=sys.stderr)
        
        all_natural_factory = self.get_factories()

        if(all_my_cyborgs > all_other_cyborgs and not len(all_natural_factory)):
            self.current_mode = 'STRENGTH'
            return self.current_mode
        if(self.factories_is_under_attack()):
            self.current_mode = 'DEFENCE'
            return self.current_mode
        self.current_mode = 'ATTACK'
        return self.current_mode
    
    def run_bot(self):
        if self.current_mode == self.modes[0]:
            self.strength_mode()
        if self.current_mode == self.modes[1]:
            return self.attack_mode()
        if self.current_mode == self.modes[2]:
            self.defence_mode()
        # if self.current_mode == self.modes[3]:
        #     return self.wait_mode()
        return self.command


    #Modes
    def strength_mode(self):
        all_my_factories,all_my_opponent_factory = self.get_factories()
        factories_with_no_cyborgs = []

        #strength factory with 0 cyborgs
        for factory in all_my_factories:
            if(factory.cyborgs == 0):
                factories_with_no_cyborgs.append(factory)
        if(factories_with_no_cyborgs):
            for factory in factories_with_no_cyborgs:
                if(factory.cyborgs> 10):
                    command = 'INC %s' % factory.id
                    self.append_command(command)
                else:
                    command = 'MOVE %s %s %s' % (self.get_my_best_factory().id, factory.id, 10)
                    self.append_command(command)

        #send 10 cyborgs with dominante factory
        if(len(all_my_opponent_factory)):
            for my_factory in all_my_factories:
                if(my_factory.cyborgs > 19 and factory.production ==3):
                    command = 'MOVE %s %s %s' % (my_factory.id, all_my_opponent_factory[0].id, 10)
                    self.append_command(command)

    def defence_mode(self):
        self.attack_with_bomb()
        factories_under_attack_details = {}
        helpers = []
        factories_under_attack = self.get_under_attack_factories()
        
        if(self.factories_is_under_attack):
            self.current_mode = self.modes[2]
            self.run_bot()
        for factory_uattack in factories_under_attack:
            factories_under_attack_details.update(self.get_factory_uattack_details(factory_uattack))
    
        for factory_uattack in factories_under_attack:
            if factories_under_attack[factory_uattack][1] == 1:
                continue
            #check for helpers
            all_my_factories = self.get_factories()[0]
            #remove factory attacked
            if(factory_uattack in all_my_factories):
                all_my_factories.remove(factory_uattack)
            for factory in all_my_factories:
                if graph.get_weight(factory.id,factories_under_attack) <= factories_under_attack_details[factory_uattack][1]:
                    helpers.append(factory)
            if len(helpers):
                for helper in helpers:
                    min_cyborgs = factories_under_attack_details[factory_uattack][1] // len(helpers)
                    command = 'Move %s %s %s' % (helper.id, factory_uattack.id, min_cyborgs)
            self.append_command(command)
        self.attack_mode()

    def attack_mode(self):
        #send a bomb
        self.attack_with_bomb()

        #get the my strongest factory
        home_base= self.get_my_best_factory()

        #get the best target
        target = self.get_target(home_base)

        #get the troops that launched
        troops_launched = self.get_track_troop_sent(home_base,target)
        if home_base != 0 and target !=0:
            if self.combined_attack(home_base,target,troops_launched)[0]:
                amount = self.combined_attack(home_base,target,troops_launched)[1]
                if amount > 0:
                    command = 'MOVE %s %s %s' % (home_base.id, target.id,amount)
                    self._add_command(command)
                else:
                    if  home_base.production < 3 and home_base.cyborgs > 10 :
                            command = 'INC %s' % home_base.id
                            self._add_command(command)
            else:
                if  home_base.production < 3 and home_base.cyborgs > 10 :
                    command = 'INC %s' % home_base.id
                    self._add_command(command)

    #Queries

    #query data by the instance
    def query_by_type(self,object):
        entities_type= []

        if(self.entities):
            for entity in self.entities:
                if isinstance(entity,object):
                    entities_type.append(entity)
            return entities_type
        else:
            return 0;

    #query all factories
    def get_factories(self):
        all_my_factories =[]
        all_opponent_factories = []
        all_netural_factory= []

        factories = self.query_by_type(Factory)
        for factory in factories:
            if factory.owner == 1:
                all_my_factories.append(factory)
            elif factory.owner == -1:
                all_opponent_factories.append(factory)
            else:
                all_netural_factory.append(factory)

        return all_my_factories, all_opponent_factories, all_netural_factory

    #query all troops
    def get_troops(self):
        all_my_troops =[]
        all_opponent_troops = []

        troops = self.query_by_type(Troop)
        for troop in troops:
            if troop.owner == 1:
                all_my_troops.append(troop)
            else:
                all_opponent_troops.append(troop)
        return all_my_troops, all_opponent_troops

   #get the closet factory from the target
    def get_factory_with_min_distance_from_target(self,target):
        min_weight = 20
        all_my_factories = self.get_factories()[0]
        for factory in all_my_factories:
            if graph.get_weight(factory.id, target.id_) < min_weight:
                home_base = factory
                min_weight = graph.get_weight(factory.id, target.id_)
        return home_base

    #get all the cyborgs in the game
    def get_cyborgs(self):
        all_my_cyborgs =0
        all_others_cyborgs = 0

        all_my_factories,all_opponent_factories,all_netural_factories =self.get_factories()

        for factory in all_my_factories:
             all_my_cyborgs += factory.cyborgs
        
        for factory in all_opponent_factories:
                all_others_cyborgs += factory.cyborgs

        return all_my_cyborgs,all_others_cyborgs
    
    #query all bombs
    def get_bombs(self):
        all_my_bombs =0
        all_others_bombs = 0

        return all_my_bombs,all_others_bombs

    def get_my_best_factory(self):
        all_my_factories = self.get_factories()[0]
        max_cyborgs_factory = 1
        best_factory = all_my_factories[0]
        if all_my_factories:
            for factory in all_my_factories:
                if factory.cyborgs > max_cyborgs_factory and factory.cyborgs > 0:
                    max_cyborgs_factory = factory.cyborgs
                    best_factory = factory
        return best_factory

    #get factories which troops on the way to them 
    def get_under_attack_factories(self):
        all_my_factories = self.get_factories()[0]
        all_opponent_troops = self.get_troops()[1]
        under_attack_factories_list = []
        
        for opponent_troop in all_opponent_troops:
            for my_factory in all_my_factories:
                if opponent_troop.dest == my_factory.id and opponent_troop.cyborgs > 0:
                    under_attack_factories_list.append(my_factory)
        return under_attack_factories_list

    #boolean attack detection method 
    def factories_is_under_attack(self):
        if self.get_under_attack_factories:
            return 1
        else:
            return 0

    #get target
    def get_target(self,home_base):
        attractive_targets = {}
        all_opponent_factories = self.get_factories()[1]
        for opponent_factory in all_opponent_factories:
            attractive_targets[opponent_factory] =self.calculate_priority(home_base,opponent_factory)
        if(len(attractive_targets) ==0):
            return 0
        return self.most_attractive_target(attractive_targets)

    #get the most attractive target by max value
    def most_attractive_target(self,dict):
        values = list(dict.values())
        keys = list(dict.keys())
        return keys[values.index(max(values))]

#Actions
    def combined_attack(self,home_base, dest, cyborgs):
        result = 0
        if dest.owner == 0:
            result = dest.cyborgs+1-cyborgs
        if(dest.owner == -1):
            result = dest.production* graph.get_weight(home_base.id, dest.id)+ dest.cyborgs+1-cyborgs
        if(result<= home_base.cyborgs):
            return 1,result
        return 0,0


    def attack_with_bomb(self):
        all_opponent_factories = self.get_factories()[0]

        #if has only 1 opponent factory
        if(len(all_opponent_factories)==1):
            if(all_opponent_factories[0].cyborgs>15 and all_opponent_factories[0].production >1):
                home_base = self.get_factory_with_min_distance_from_target(all_opponent_factories[0])
                command = 'BOMB %s %s' % (home_base.id_, all_opponent_factories[0].id)
                self._add_command(command)
        if len(all_opponent_factories) > 1:
            for factory in all_opponent_factories:
                if factory.cyborgs and factory.production >= 2:
                    home_base = self.__get_the_closest_home_base(factory)
                    if home_base:
                        command = 'BOMB %s %s' % (home_base.id_, factory.id)
                        self._add_command(command)


    #get details about attack: how long, and how much cyborgs
    def get_factory_uattack_details(self,factory_uattack):
        cyborgs_var = 0
        all_my_troops ,all_opponent_troops = self.get_troops()
        all_my_factories = self.get_factories()[0]
        opp_troops_aimed_to_my_factories =[]
        my_troops_aimed_to_my_factories =[]
        if len(all_opponent_troops)>0:
            for troop in all_opponent_troops:
                for factory in all_my_factories:
                    if(factory.id == troop.dest):
                        opp_troops_aimed_to_my_factories.append(troop)
        if len(all_my_troops)>0:
            for troop in all_my_troops:
                for factory in all_my_factories:
                    if(factory.id == troop.dest):
                        my_troops_aimed_to_my_factories.append(troop)
        
        
        for i in range(self.MAX_TURNS_FOR_TROOP):
            cyborgs_var = factory_uattack.cyborgs
           
            #my troops calculation
            for troop in my_troops_aimed_to_my_factories:
                for j in range(i):
                    if troop.remaining_turns == j:
                        cyborgs_var += troop.cyborgs

            #opponent troops calculation
            for troop in opp_troops_aimed_to_my_factories:
                for j in range(i):
                    if troop.remaining_turns == j:
                        cyborgs_var -= troop.cyborgs
            
            #future calculation after 20 turns
            if cyborgs_var <= 0:
                print("LOG: entities leng %s"%cyborgs_var, file=sys.stderr)
                return{factory_uattack:[cyborgs_var,i]}

    def calculate_priority(self,my_factory,traget_factory):
        sum = traget_factory.cyborgs * -20
        sum += traget_factory.production * 100
        sum += graph.get_weight(my_factory.id, traget_factory.id) * -20
        if traget_factory.id == -1:
            sum += -50
    
    def get_track_troop_sent(self,home_base,traget):
        result= [0,0]
        all_my_troops = self.get_troops()[0]
        for troop in all_my_troops():
            if troop.source == home_base.id and troop.dest == traget.id:
                result[0] = 1
                result[1] += troop.cyborgs
        return result
        
#---main---
factory_count = int(input())
link_count = int(input())

graph = IndirectedGraph()
for i in range(link_count):
    factory_1, factory_2, distance = [int(j) for j in input().split()]
    graph.add_connection(factory_1, factory_2, distance)


#start game
while True:
    entity_count = int(input())
    data = CentralRepository()
    for _ in range(entity_count):
        entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
        if(entity_type == 'FACTORY'):
            data.add_entity(Factory(int(entity_id),
                                  int(arg_1), int(arg_2), int(arg_3), int(arg_4)))
        elif(entity_type == 'TROOP'):
            data.add_entity(Troop(int(entity_id),
                                  int(arg_1), int(arg_2), int(arg_3), int(arg_4),int(arg_5)))
        elif(entity_type == 'BOMB'):
            data.add_entity(Bomb(int(entity_id),
                                  int(arg_1), int(arg_2), int(arg_3), int(arg_4)))

    bot = Bot(data.get_entities())
    bot.set_bot_mode()
    print("MSG %s"%bot.current_mode)
    output = bot.run_bot()
    print("LOG:output: %s"%bot.current_mode,output, file=sys.stderr)
    print("LOG:current_mode: %s"%bot.current_mode, file=sys.stderr)
    if output == '':
        print('Wait')
    else:
        if output[len(output) - 1] == ';':
            output = output[len(output) - 1]
        print(output)