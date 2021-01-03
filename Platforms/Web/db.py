from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from Utils.Classes.webuser import WebUser
from Utils.Classes.webrole import WebRole

# users
async def getWebUsers(cls:"PhaazebotWeb", **search) -> List[WebUser]:
	"""
	Get web users
	Returns a list of WebUserInfo()

	Optional search keywords:
	-------------------------
	* `user_id` - Union[int, str, None] : (Default: None) [sets LIMIT to 1]
	* username `str`: (Default: None)
	* username_contains `str`: (Default: None) [DB uses LIKE]
	* email `str`: (Default: None)
	* email_contains `str`: (Default: None) [DB uses LIKE]
	* verified `int`: (Default: 0) [0=all, 1=only verified, 2=only not verified]
	* order_str `str`: (Default: "ORDER BY user.id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	* where `str`: (Default: None) [Overwrites everything]
	* where_values `tuple` or `dict`: (Default: None) [Only needed if where != None]
	"""
	username:str = search.get("username", None)
	username_contains:str = search.get("username_contains", None)
	email:str = search.get("email", None)
	email_contains:str = search.get("email_contains", None)
	verified:int = search.get("verified", 0)
	order_str:str = search.get("order_str", "ORDER BY `user`.`id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)
	where:str = search.get("where", None)
	where_values:tuple = search.get("where_values", ())

	ground_sql:str = f"""
		SELECT
			`user`.*,
			GROUP_CONCAT(`role`.`name` SEPARATOR ';;;') AS `roles`
		FROM `user`
		LEFT JOIN `user_has_role`
			ON `user_has_role`.`user_id` = `user`.`id`
		LEFT JOIN `role`
			ON `role`.`id` = `user_has_role`.`role_id`
		WHERE 1=1"""
	ground_values:tuple = ()

	sql:str = ""
	values:tuple = ()

	user_id:Union[int, str, None] = search.get("user_id", None)
	if user_id:
		sql += " AND `user`.`id` = %s"
		values += (int(user_id),)
		search["limit"] = 1

	if username and not where:
		sql += " AND `user`.`username` = %s"
		values += (str(username),)

	if username_contains and not where:
		username_contains = f"%{username_contains}%"
		sql += " AND `user`.`username` LIKE %s"
		values += (str(username_contains),)

	if email and not where:
		sql += " AND `user`.`email` = %s"
		values += (str(email),)

	if email_contains and not where:
		email_contains = f"%{email_contains}%"
		sql += " AND `user`.`email` LIKE %s"
		values += (str(email_contains),)

	if verified == 1 and not where:
		sql += " AND `user`.`verified` = 1"
	if verified == 2 and not where:
		sql += " AND `user`.`verified` = 0"

	if where:
		sql += f" AND {where}"
		values = where_values

	sql += " GROUP BY `user`.`id`" # add group by for concat

	if order_str:
		sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, ground_values+values)
	return [WebUser(x) for x in res]

async def getWebUserAmount(cls:"PhaazebotWeb", where:str="1=1", values:tuple=()) -> int:
	"""
	simply gives a number of all matched user
	"""
	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(f"SELECT COUNT(*) AS `I` FROM `user` WHERE {where}", values)

	return res[0]['I']

# roles
async def getWebRoles(cls:"PhaazebotWeb", **search) -> List[WebRole]:
	"""
	Get roles the a web user can have
	Returns a list of WebRole()

	Optional keywords:
	------------------
	* role_id `str` or `int` : (Default: None)
	* user_id `str` or `int` : (Default: None) [Get all roles a user has]
	* name `str`: (Default: None)
	* name_contains `str`: (Default: None) [DB uses LIKE]
	* can_be_removed `int`: (Default: 0) [0=all, 1=only removable, 2=only not removable]
	* order_str `str`: (Default: "ORDER BY role.id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	* where `str`: (Default: None) [Overwrites everything]
	* where_values `tuple` or `dict`: (Default: None) [Only needed if where != None]
	"""
	role_id:str or int = search.get("role_id", None)
	user_id:str or int = search.get("user_id", None)
	name:str = search.get("name", None)
	name_contains:str = search.get("name_contains", None)
	can_be_removed:int = search.get("can_be_removed", 0)
	order_str:str = search.get("order_str", "ORDER BY `role`.`id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)
	where:str = search.get("where", None)
	where_values:tuple = search.get("where_values", ())

	sql:str = f"""SELECT `role`.* FROM `role` WHERE 1=1"""
	values:tuple = ()

	if user_id:
		sql = """
			SELECT `role`.*
			FROM `user_has_role`
			LEFT JOIN `role` ON `role`.`id` = `user_has_role`.`role_id`
			WHERE `user_has_role`.`user_id` = %s"""
		values = (int(user_id),)

	if role_id and not where:
		sql += " AND `role`.`id` = %s"
		values += (int(role_id),)

	if name and not where:
		sql += " AND `role`.`name` = %s"
		values += (str(name),)

	if name_contains and not where:
		name_contains = f"%{name_contains}%"
		sql += " AND `role`.`name` LIKE %s"
		values += (str(name_contains),)

	if can_be_removed == 1 and not where:
		sql += " AND `role`.`can_be_removed` = 1"
	if can_be_removed == 2 and not where:
		sql += " AND `role`.`can_be_removed` = 0"

	if where:
		sql += f" AND {where}"
		values = where_values

	if order_str:
		sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(sql, values)
	return [WebRole(x) for x in res]

async def getWebRoleAmount(cls:"PhaazebotWeb", where:str="1=1", values:tuple=()) -> int:
	"""
	simply gives a number of all matched roles
	"""
	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(f"SELECT COUNT(*) AS `I` FROM `role` WHERE {where}", values)

	return res[0]['I']
