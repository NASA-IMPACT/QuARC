import sys
from utils import update_parameter, ssm_param_name

update_parameter(ssm_param_name, sys.argv[1])
