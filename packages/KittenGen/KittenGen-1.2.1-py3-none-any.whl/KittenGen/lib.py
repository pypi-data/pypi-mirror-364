import random
import math
import string
import cyaron


global_vars = {
    'random': random.random,
    'randint': random.randint,
    'uniform': random.uniform,
    'choice': random.choice,
    'sample': random.sample,
    'seed': random.seed,
    'randrange': random.randrange,
    'math': math,
    'ascii_lowercase': string.ascii_lowercase,
    'ascii_uppercase': string.ascii_uppercase,
    'digits': string.digits,
    'ascii_letters': string.ascii_letters,
    'cyaron': cyaron,
    'Graph': cyaron.Graph,
    'Polygon': cyaron.Polygon,
    'Vector': cyaron.Vector,
    'String': cyaron.String,
    'Sequence': cyaron.Sequence,
    'Edge': cyaron.Edge,
}
