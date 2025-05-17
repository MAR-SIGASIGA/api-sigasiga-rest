from .. import db
class Sport(db.Model):
    __tablename__ = "sports"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    scoreboard = db.Column(db.JSON, nullable=True)
    statistics = db.Column(db.JSON, nullable=True)

    @staticmethod
    def get_sports_list():
        sports = Sport.query.all()
        sports_list = []
        for sport in sports:
            sports_list.append({
                "id": sport.id,
                "name": sport.name,
                "slug": sport.slug,
                "scoreboard": sport.scoreboard,
                "statistics": sport.statistics
            })
        return sports_list

    @staticmethod
    def get_sport_by_id(sport_id):
        sport = Sport.query.filter_by(id=sport_id).first()
        if sport:
            return {
                "id": sport.id,
                "name": sport.name,
                "slug": sport.slug,
                "scoreboard": sport.scoreboard,
                "statistics": sport.statistics
            }
        return None