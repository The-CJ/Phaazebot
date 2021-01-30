from typing import TYPE_CHECKING, List, Union, Optional
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from Utils.Classes.webuser import WebUser
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED

# user
async def getWebUsers(cls:"PhaazebotWeb", **search) -> Union[List[WebUser], int]:
	"""
	Get web users
	Returns a list of WebUser()

	Optional 'search' keywords:
	---------------------------
	* `user_id` - Union[int, str, UNDEFINED] : (Default: UNDEFINED) [sets LIMIT to 1]
	* `username` - Union[str, UNDEFINED] : (Default: UNDEFINED)
	* `email` - Union[str, None, UNDEFINED] : (Default: UNDEFINED)
	* `verified` - Union[int, UNDEFINED] : (Default: UNDEFINED) [0=only not verified, 1=only verified]

	Optional 'contains' keywords:
	-----------------------------
	* `username_contains` - Union[str, UNDEFINED] : (Default: UNDEFINED) [DB uses LIKE on `username`]
	* `email_contains` - Union[str, UNDEFINED] : (Default: UNDEFINED) [DB uses LIKE on `email`]

	Optional 'between' keywords:
	----------------------------
	* `created_at_between` - Tuple[from:str, to:str] : (Default: None) [DB uses >= and <=]
	* `edited_at_between` - Tuple[from:str, to:str] : (Default: None) [DB uses >= and <=]
	* `last_login_between` - Tuple[from:str, to:str] : (Default: None) [DB uses >= and <=]
	* `username_changed_between` - Tuple[from:int, to:int] : (Default: None) [DB uses >= and <=]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY user.id ASC")
	* `limit` - int : (Default: 0)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
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
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	user_id:Union[int, str, UNDEFINED] = search.get("user_id", UNDEFINED)
	if user_id != UNDEFINED:
		sql += " AND `user`.`id` = %s"
		values += (int(user_id),)
		search["limit"] = 1

	username:Union[str, UNDEFINED] = search.get("username", UNDEFINED)
	if username != UNDEFINED:
		sql += " AND `user`.`username` = %s"
		values += (str(username),)

	email:Union[str, UNDEFINED] = search.get("email", UNDEFINED)
	if email != UNDEFINED:
		sql += " AND `user`.`email` = %s"
		values += (str(email),)

	verified:Union[int, UNDEFINED] = search.get("email", UNDEFINED)
	if email != UNDEFINED:
		sql += " AND `user`.`verified` = %s"
		values += (int(verified),)

	# Optional 'contains' keywords
	username_contains:Union[str, UNDEFINED] = search.get("username_contains", UNDEFINED)
	if username_contains != UNDEFINED:
		username_contains = f"%{username_contains}%"
		sql += " AND `user`.`username` LIKE %s"
		values += (str(username_contains),)

	email_contains:Union[str, UNDEFINED] = search.get("email_contains", UNDEFINED)
	if email_contains != UNDEFINED:
		email_contains = f"%{email_contains}%"
		sql += " AND `user`.`email` LIKE %s"
		values += (str(email_contains),)

	# Optional 'between' keywords
	created_at_between:Optional[tuple] = search.get("created_at_between", None)
	if created_at_between is not None:
		from_:Optional[str] = created_at_between[0]
		to_:Optional[str] = created_at_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `user`.`created_at` BETWEEN %s AND %s"
			values += (str(from_), str(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `user`.`created_at` >= %s"
			values += (str(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `user`.`created_at` <= %s"
			values += (str(to_),)

	edited_at_between:Optional[tuple] = search.get("edited_at_between", None)
	if edited_at_between is not None:
		from_:Optional[str] = edited_at_between[0]
		to_:Optional[str] = edited_at_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `user`.`edited_at` BETWEEN %s AND %s"
			values += (str(from_), str(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `user`.`edited_at` >= %s"
			values += (str(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `user`.`edited_at` <= %s"
			values += (str(to_),)

	last_login_between:Optional[tuple] = search.get("last_login_between", None)
	if last_login_between is not None:
		from_:Optional[str] = last_login_between[0]
		to_:Optional[str] = last_login_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `user`.`last_login` BETWEEN %s AND %s"
			values += (str(from_), str(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `user`.`last_login` >= %s"
			values += (str(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `user`.`last_login` <= %s"
			values += (str(to_),)

	username_changed_between:Optional[tuple] = search.get("username_changed_between", None)
	if username_changed_between is not None:
		from_:Optional[int] = username_changed_between[0]
		to_:Optional[int] = username_changed_between[1]

		if (from_ is not None) and (to_ is not None):
			sql += " AND `user`.`username_changed` BETWEEN %s AND %s"
			values += (int(from_), int(to_))

		if (from_ is not None) and (to_ is None):
			sql += " AND `user`.`username_changed` >= %s"
			values += (int(from_),)

		if (from_ is None) and (to_ is not None):
			sql += " AND `user`.`username_changed` <= %s"
			values += (int(to_),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = 0
		search["offset"] = 0
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `user`
			WHERE 1 = 1"""

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

	limit:int = search.get("limit", 0)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [WebUser(x) for x in res]

# roles
async def getWebRoles(cls:"PhaazebotWeb", **search) -> Union[List[WebRole], int]:
	"""
	Get roles the a web user can have
	Returns a list of WebRole()

	Optional 'search' keywords:
	---------------------------
	* `role_id` - Union[int, str, UNDEFINED] : (Default: UNDEFINED) [sets LIMIT to 1]
	* `name` - Union[str, UNDEFINED] : (Default: UNDEFINED)
	* `can_be_removed` - Union[int, UNDEFINED] : (Default: UNDEFINED) [0 = only not removable, 1 = only removable]

	Optional 'contains' keywords:
	-----------------------------
	* `name_contains` - Union[str, UNDEFINED] : (Default: UNDEFINED) [DB uses LIKE on `name`]
	* `description_contains` - Union[str, UNDEFINED] : (Default: UNDEFINED) [DB uses LIKE on `description`]

	Other:
	------
	* `order_str` - str : (Default: "ORDER BY role.id ASC")
	* `limit` - Union[int, UNDEFINED] : (Default: UNDEFINED)
	* `offset` - int : (Default: 0)

	Special:
	--------
	* `count_mode` - bool : (Default: False)
		* [returns COUNT(*) as int, disables: `limit`, `offset`]
	* `overwrite_where` - Optional[str] : (Default: None)
		* [Overwrites everything, appended after "1=1", so start with "AND field = %s"]
		* [Without `limit`, `offset`, `order` and `group by`]
	* `overwrite_where_values` - Union[tuple, dict, None] : (Default: ())
	"""
	ground_sql:str = f"""
		SELECT `role`.*
		FROM `role`
		WHERE 1 = 1"""

	sql:str = ""
	values:tuple = ()

	# Optional 'search' keywords
	role_id:Union[int, str, UNDEFINED] = search.get("role_id", UNDEFINED)
	if role_id != UNDEFINED:
		sql += " AND `role`.`id` = %s"
		values += (int(role_id),)
		search["limit"] = 1

	name:Union[str, UNDEFINED] = search.get("name", UNDEFINED)
	if name != UNDEFINED:
		sql += " AND `role`.`name` = %s"
		values += (str(name),)

	can_be_removed:Union[int, UNDEFINED] = search.get("can_be_removed", UNDEFINED)
	if can_be_removed != UNDEFINED:
		sql += " AND `role`.`can_be_removed` = %s"
		values += (int(can_be_removed),)

	# Optional 'contains' keywords
	name_contains:Union[str, UNDEFINED] = search.get("name_contains", UNDEFINED)
	if name_contains != UNDEFINED:
		name_contains = f"%{name_contains}%"
		sql += " AND `role`.`name` LIKE %s"
		values += (str(name_contains),)

	description_contains:Union[str, UNDEFINED] = search.get("description_contains", UNDEFINED)
	if description_contains != UNDEFINED:
		description_contains = f"%{description_contains}%"
		sql += " AND `role`.`email` description %s"
		values += (str(description_contains),)

	# Special
	count_mode:bool = search.get("count_mode", False)
	if count_mode:
		search["limit"] = 0
		search["offset"] = 0
		ground_sql: str = """
			SELECT COUNT(*) AS `I`
			FROM `role`
			WHERE 1 = 1"""

	overwrite_where:Optional[str] = search.get("overwrite_where", None)
	overwrite_where_values:Union[tuple, dict, None] = search.get("overwrite_where_values", None)
	if overwrite_where:
		sql = overwrite_where
		values = overwrite_where_values

	# Other
	order_str:str = search.get("order_str", "ORDER BY `role`.`id` ASC")
	sql += f" {order_str}"

	limit:int = search.get("limit", 0)
	offset:int = search.get("offset", 0)
	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.BASE.PhaazeDB.selectQuery(ground_sql+sql, values)

	if count_mode:
		return res[0]['I']
	else:
		return [WebRole(x) for x in res]
