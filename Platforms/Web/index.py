from aiohttp.web import RouteTableDef

# This class in imported in all entry points.
# And then linked via decorator
PhaazeWebIndex:RouteTableDef = RouteTableDef()
