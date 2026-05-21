from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()


@traceable(name="k8s_incident_analysis")
def traced_analysis(func, *args, **kwargs):
    return func(*args, **kwargs)