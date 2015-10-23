


# Item削除時の挙動
Item-Xの削除はRecommender().remove_goods(Item-X)で実施できる。
Item-Xを削除したとき、Item-AでレコメンドされているItem-Xは消えない
レコメンドする商品からItem-Xを削除するには2つの方法がある。

1. Item-Aが新しく購入されたとき
Item-Aが新しく購入(Recommender().like())されたときレコメンドする商品が
再生成されるため、Item-AのレコメンドからItem-Xが消える

2. 全てのレコメンドする商品一覧を更新する
Recommender().update_all()を実行する。
Item数x約100ms実行に掛かるので注意すること



