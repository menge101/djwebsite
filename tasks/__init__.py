from invoke import Collection
from tasks import data

ns = Collection()
ns.add_collection(data.data, "data")
