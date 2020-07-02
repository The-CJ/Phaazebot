from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from Utils.Classes.webuserinfo import WebUserInfo

async def getWebUsers(cls:"WebIndex", **search:dict) -> List[WebUserInfo]:
	"""
	Get web users
	Returns a list of WebUserInfo()

	Optional keywords:
	------------------
	* user_id `str` or `int` : (Default: None)
	* username `str`: (Default: None)
	* username_contains `str`: (Default: None) [DB uses LIKE]
	* email `str`: (Default: None)
	* email_contains `str`: (Default: None) [DB uses LIKE]
	* verified `int`: (Default: 0) [0=all, 1=only verified, 2=only not verified]
	* order_str `str`: (Default: "ORDER BY user.id")
	* limit `int`: (Default: None)
	* offset `int`: (Default: 0)
	"""
	user_id:str or int = search.get("user_id", None)
	username:str = search.get("username", None)
	username_contains:str = search.get("username_contains", None)
	email:str = search.get("email", None)
	email_contains:str = search.get("email_contains", None)
	verified:int = search.get("verified", 0)
	order_str:str = search.get("order_str", "ORDER BY `user`.`id`")
	limit:int = search.get("limit", None)
	offset:int = search.get("offset", 0)

	sql:str = f"""
		SELECT
			`user`.*,
			GROUP_CONCAT(`role`.`name` SEPARATOR ';;;') AS `roles`
		FROM `user`
		LEFT JOIN `user_has_role`
			ON `user_has_role`.`user_id` = `user`.`id`
		LEFT JOIN `role`
			ON `role`.`id` = `user_has_role`.`role_id`
		WHERE 1=1"""
	values:tuple = ()

	if user_id:
		sql += " AND `user`.`id` = %s"
		values += ( int(user_id), )

	if username:
		sql += " AND `user`.`username` = %s"
		values += ( str(username), )

	if username_contains:
		username_contains = f"%{username_contains}%"
		sql += " AND `user`.`username` LIKE %s"
		values += ( str(username_contains), )

	if email:
		sql += " AND `user`.`email` = %s"
		values += ( str(email), )

	if email_contains:
		email_contains = f"%{email_contains}%"
		sql += " AND `user`.`email` LIKE %s"
		values += ( str(email_contains), )

	if verified == 1:
		sql += " AND `user`.`verified` = 1"
	if verified == 2:
		sql += " AND `user`.`verified` = 0"

	sql += " GROUP BY `user`.`id`" # add group by for concat

	if order_str:
		sql += f" {order_str}"

	if limit:
		sql += f" LIMIT {limit}"
		if offset:
			sql += f" OFFSET {offset}"

	res:List[dict] = cls.Web.BASE.PhaazeDB.selectQuery(sql, values)

	return_list:List[WebUserInfo] = []
	for user in res:
		WebUser:WebUserInfo = WebUserInfo(cls.Web.BASE, None)
		await WebUser.finishUser(user)
		return_list.append(WebUser)

	return return_list

async def getWebUserAmount(cls:"WebIndex", where:str="1=1", values:tuple=()) -> int:
	"""
	simply gives a number of all matched user
	"""
	res:List[dict] = cls.Web.BASE.PhaazeDB.selectQuery(f"SELECT COUNT(*) AS `I` FROM `user` WHERE {where}", values)

	return res[0]['I']
