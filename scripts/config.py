DISTANCE_TOLERANCE = 0.005
SIMULATION_SPEED = 100

MAX_SIMULATION_TIME = 1000
MAX_SERVICED_TASKS = 1000
NUM_ACTORS = 1
ACTOR_SPEED = 1
LAMBDA = 0.8
SERVICE_TIME = 0
TICK_TIME = 0.01
BETA = 0.712    # constant for TSP length

DEFAULT_POLICY_NAME = "random_assgn"
DEFAULT_GENERATOR_NAME = "uniform"
GENERATOR_ARGS = {
    'min': 0,
    'max': 1,
    'distributions': [
        [0.75, 0.1],
        [0.25, 0.1]
    ],
    'seed': None,
    'dim': 2,
    'mix': 0.5,
}
SHOW_SIM = False

DEFAULT_POLICY_COST_EXPONENT = 2
DEFAULT_POLICY_ETA = 1            # proportion of the batch tsp path to execute (0,1]
DEFAULT_POLICY_GAMMA = 0.9        # batch insertion threshold -- insertion after this point are rejected until next replan [0,1)

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_MARGIN = 120

SCREEN_OUTLINE_COLOUR = (0, 0, 0, 80)
SCREEN_BACKGROUND_COLOUR = (255, 255, 255, 255)
ACTOR_COMPLETE_PATH_COLOUR = (220, 220, 220, 255)
ACTOR_COLOUR = (100, 100, 240, 255)
ACTOR_PATH_COLOUR = (40, 40, 40, 255)
ACTOR_PATH_WIDTH = 3
STATUS_FONT_COLOUR = (0, 0, 0, 255)
STATUS_FONT_SIZE = 32

STATUS_Y_SIZE = 100
STATUS_YMARGIN = 8
STATUS_X_SIZE = 300
STATUS_XMARGIN = 16

RESULTS_DIR = 'results'
TASKS_DIR = 'tasks'

TASK_LIST_FILE_PREFIX = "dvrp_tasks"
