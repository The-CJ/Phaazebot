from typing import TYPE_CHECKING, List, Union, Optional
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from Utils.Classes.webuser import WebUser
from Utils.Classes.webrole import WebRole

# users
async def getWebUsers(cls:"PhaazebotWeb", **search) -> List[WebUser]:
	"""
	Get web users
	Returns a list of WebUser()

	Optional 'search' keywords:
	---------------------------
	* `user_id` - Union[int, str, None] : (Default: None) [sets LIMIT to 1]
	* `username` - Optional[str] : (Default: None)
	* `email` - Optional[str] : (Default: None)
	* `verified` - Optional[int] : (Default: None) [0=only not verified, 1=only verified]

	Optional 'contains' keywords:
	-----------------------------
	* `username_contains` - Optional[str] : (Default: None) [DB uses LIKE on `username`]
	* `email_contains` - Optional[str] : (Default: None) [DB uses LIKE on `email`]

	Other
	-------
	* `order_str` - str : (Default: "ORDER BY user.id ASC")
	* `limit` - Optional[int] : (Default: None)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
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

	# Optional 'search' keywords
	user_id:Union[int, str, None] = search.get("user_id", None)
	if user_id:
		sql += " AND `user`.`id` = %s"
		values += (int(user_id),)
		search["limit"] = 1

	username:Optional[str] = search.get("username", None)
	if username:
		sql += " AND `user`.`username` = %s"
		values += (str(username),)

	email:Optional[str] = search.get("email", None)
	if email:
		sql += " AND `user`.`email` = %s"
		values += (str(email),)

	verified:Optional[int] = search.get("email", None)
	if email:
		sql += " AND `user`.`verified` = %s"
		values += (int(verified),)

	# Optional 'contains' keywords
	username_contains:Optional[str] = search.get("username_contains", None)
	if username_contains:
		username_contains = f"%{username_contains}%"
		sql += " AND `user`.`username` LIKE %s"
		values += (str(username_contains),)

	email_contains:Optional[str] = search.get("email_contains", None)
	if email_contains:
		email_contains = f"%{email_contains}%"
		sql += " AND `user`.`email` LIKE %s"
		values += (str(email_contains),)

	# Special
	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", None)
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# add group by for GROUP_CONCAT
	sql += " GROUP BY `user`.`id`"

	# Other
	order_str:str = search.get("order_str", "ORDER BY `user`.`id` ASC")
	sql += f" {order_str}"

	limit:Optional[int] = search.get("limit", None)
	offset:int = search.get("offset", 0)
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
