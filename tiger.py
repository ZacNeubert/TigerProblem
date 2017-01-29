#Configuration

horizon = 2
gold_u = 20
tiger_u = -100
listen_u = -1

listen_correct_prob = .90

continue_acting_after_tiger_attack = False
players_cooperate = False

# English: If my sureness is greater than the ratio of consequences to rewards, I will open the door
gold_tiger_ratio = abs((abs(tiger_u) + listen_u*2)/(gold_u+abs(tiger_u)+listen_u*2))


# Cosmetic Functions
def readable_listens(listens):
    return ['Left' if l else 'Right' for l in listens]

def larger_sureness(left_sureness, right_sureness):
    if left_sureness == right_sureness:
        return 'Even Bias'
    return str(right_sureness*100)+'% bias for right' if right_sureness > left_sureness else str(left_sureness*100)+'% bias for left'

#Helpers
def product(l):
    p = 1
    for i in l:
        p*=i
    return p

#def get_sureness(listens):
#    corrects = len([l for l in listens if l])
#    return corrects/len(listens)
def get_sureness(listens):
    corrects = len([l for l in listens if l])
    incorrects = corrects - len(listens)
    if corrects == 0:
        return abs((1-listen_correct_prob)/incorrects)
    if incorrects == 0:
        return 1-((1-listen_correct_prob)/corrects)
    correctProb = 1-((1-listen_correct_prob)/corrects)
    incorrectProb = (1-listen_correct_prob)/incorrects
    return (correctProb*corrects + incorrectProb*incorrects)/len(listens)

#Main
def event(level, p1listens, p2listens, utility):
    listens = p1listens+p2listens
    if level == horizon:
        chance_of_occurrence = product([1-listen_correct_prob if l else listen_correct_prob for l in listens])
        
        p1left_sureness = get_sureness(p1listens)
        p1right_sureness = get_sureness([not l for l in p1listens])
        
        p2left_sureness = get_sureness(p2listens)
        p2right_sureness = get_sureness([not l for l in p2listens])
        
        left_sureness = get_sureness(listens)
        right_sureness = get_sureness([not l for l in listens])
        sure_left = left_sureness > gold_tiger_ratio 
        sure_right = right_sureness > gold_tiger_ratio 

        assert not (sure_left and sure_right)

        if players_cooperate:
            if sure_left:
                utility += tiger_u
                print('Eaten by tiger')
            elif sure_right:
                utility += gold_u
                print('Got gold!')
            else:
                utility += listen_u*2
                print('Not opening door')

            print('\tP1 Heard:',readable_listens(p1listens),
                    larger_sureness(p1left_sureness,p1right_sureness),
                    '\n\tP2 Heard:',readable_listens(p2listens),
                    larger_sureness(p2left_sureness,p2right_sureness),
                    '\n\tTogether heard:',readable_listens(listens),
                    larger_sureness(left_sureness, right_sureness),
                    '\n\tUtility:',utility,
                    '\n\tChance of occurrence: {:2.4f}%'.format(chance_of_occurrence*100))
            return utility*chance_of_occurrence
        else: # Players act independently
            eaten=False
            p1_sure_left = p1left_sureness > gold_tiger_ratio 
            p1_sure_right = p1right_sureness > gold_tiger_ratio 
            p2_sure_left = p2left_sureness > gold_tiger_ratio
            p2_sure_right = p2right_sureness > gold_tiger_ratio

            assert not (p1_sure_left and p1_sure_right)
            assert not (p2_sure_left and p2_sure_right)

            p1_acts = p1_sure_left or p1_sure_right
            p2_acts = p2_sure_left or p2_sure_right

            if p1_sure_left or p2_sure_left:
                print('Eaten by tiger')
                utility = tiger_u + utility
                eaten=True
            if p1_sure_right or p2_sure_right:
                if not eaten or continue_acting_after_tiger_attack:
                    print('Got gold!')
                    utility = gold_u + utility
            if not p1_acts:
                if not eaten or continue_acting_after_tiger_attack:
                    print('P1 Not opening door')
                    utility += listen_u
            if not p2_acts:
                if not eaten or continue_acting_after_tiger_attack:
                    print('P2 Not opening door')
                    utility += listen_u
            print('\tP1 Heard:',readable_listens(p1listens),larger_sureness(p1left_sureness,p1right_sureness),
                    '\n\tP2 Heard:',readable_listens(p2listens),larger_sureness(p2left_sureness,p2right_sureness),
                    '\n\tUtility:',utility,
                    '\n\tChance of occurrence: {:2.4f}%'.format(chance_of_occurrence*100))
            return utility*chance_of_occurrence
    else:
        listen2wrong = event(level+1, p1listens+[False], p2listens+[False], utility+listen_u*2)
        listen2right = event(level+1, p1listens+[True], p2listens+[True], utility+listen_u*2)
        listenrightwrong = event(level+1, p1listens+[True], p2listens+[False], utility+listen_u*2)
        listenwrongright = event(level+1, p1listens+[False], p2listens+[True], utility+listen_u*2)
        return sum([listen2wrong, listen2right, listenrightwrong, listenwrongright])

if __name__ == '__main__':
    print('Average Payout: {:4.4f}'.format(event(0, [], [], 0)))
    print('horizon:',horizon)
    print('gold_u:',gold_u)
    print('tiger_u:',tiger_u)
    print('listen_u:',listen_u)
    print('listen_correct_prob:',listen_correct_prob)
    print('continue_acting_after_tiger_attack:',continue_acting_after_tiger_attack)
    print('players_cooperate:',players_cooperate)
    print('Open Threshold:',gold_tiger_ratio)
