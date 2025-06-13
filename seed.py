from app import app
from models import db, Topic, Suggestion

with app.app_context():
    db.drop_all()
    db.create_all()

    # 3 Topic Positif untuk Type A
    topic1 = Topic(topic_type='A', sentiment='positif', title='Topik 1')
    topic2 = Topic(topic_type='A', sentiment='positif', title='Topik 2')
    topic3 = Topic(topic_type='A', sentiment='positif', title='Topik 3')

    # 3 Topic Negatif untuk Type A
    topic4 = Topic(topic_type='A', sentiment='negatif', title='Topik 1')
    topic5 = Topic(topic_type='A', sentiment='negatif', title='Topik 2')
    topic6 = Topic(topic_type='A', sentiment='negatif', title='Topik 3')

    # 3 Topic Positif untuk Type B
    topic7 = Topic(topic_type='B', sentiment='positif', title='Topik 1')
    topic8 = Topic(topic_type='B', sentiment='positif', title='Topik 2')
    topic9 = Topic(topic_type='B', sentiment='positif', title='Topik 3')

    # 3 Topic Negatif untuk Type B
    topic10 = Topic(topic_type='B', sentiment='negatif', title='Topik 1')
    topic11 = Topic(topic_type='B', sentiment='negatif', title='Topik 2')
    topic12 = Topic(topic_type='B', sentiment='negatif', title='Topik 3')

    # 4 Topic Positif untuk Type C
    topic13 = Topic(topic_type='C', sentiment='positif', title='Topik 1')
    topic14 = Topic(topic_type='C', sentiment='positif', title='Topik 2')
    topic15 = Topic(topic_type='C', sentiment='positif', title='Topik 3')
    topic16 = Topic(topic_type='C', sentiment='positif', title='Topik 4')

    # 2 Topic Negatif untuk Type C
    topic17 = Topic(topic_type='C', sentiment='negatif', title='Topik 1')
    topic18 = Topic(topic_type='C', sentiment='negatif', title='Topik 2')

    # 7 Topic Positif untuk Type D
    topic19 = Topic(topic_type='D', sentiment='positif', title='Topik 1')
    topic20 = Topic(topic_type='D', sentiment='positif', title='Topik 2')
    topic21 = Topic(topic_type='D', sentiment='positif', title='Topik 3')
    topic22 = Topic(topic_type='D', sentiment='positif', title='Topik 4')
    topic23 = Topic(topic_type='D', sentiment='positif', title='Topik 5')
    topic24 = Topic(topic_type='D', sentiment='positif', title='Topik 6')
    topic25 = Topic(topic_type='D', sentiment='positif', title='Topik 7')

    # 2 Topic Negatif untuk Type D
    topic26 = Topic(topic_type='D', sentiment='negatif', title='Topik 1')
    topic27 = Topic(topic_type='D', sentiment='negatif', title='Topik 2')

    db.session.add_all([
        topic1, topic2, topic3, topic4, topic5, topic6,
        topic7, topic8, topic9, topic10, topic11, topic12,
        topic13, topic14, topic15, topic16, topic17, topic18,
        topic19, topic20, topic21, topic22, topic23, topic24, topic25,
        topic26, topic27
    ])

    # Konten lorem acak
    lorem_contents = [
        "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna.",
        "Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat dolore.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur lorem ipsum.",
        "Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum lorem.",
        "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium totam rem aperiam.",
        "Eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo dolore dolorem.",
        "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit sed quia consequuntur magni dolores eos.",
        "Neque porro quisquam est qui dolorem ipsum quia dolor sit amet consectetur adipisci velit lorem ipsum dolor sit.",
        "Ut enim ad minima veniam quis nostrum exercitationem ullam corporis suscipit laboriosam nisi ut aliquid ex ea commodi.",
        "Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur lorem ipsum.",
        "Vel illum qui dolorem eum fugiat quo voluptas nulla pariatur at vero eos et accusamus et iusto odio dignissimos.",
        "Deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident similique sunt.",
        "Nam libero tempore cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere.",
        "Facilis est et expedita distinctio nam libero tempore cum soluta nobis est eligendi optio voluptate velit esse quam.",
        "Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae.",
        "Sint et molestiae non recusandae itaque earum rerum hic tenetur a sapiente delectus ut aut reiciendis voluptatibus.",
    ]

    # Buat suggestions 2 per topik dari type A–D
    from random import sample
    suggestions = []
    for topic in [
        topic1, topic2, topic3, topic4, topic5, topic6,
        topic7, topic8, topic9, topic10, topic11, topic12,
        topic13, topic14, topic15, topic16, topic17, topic18,
        topic19, topic20, topic21, topic22, topic23, topic24, topic25,
        topic26, topic27
    ]:
        selected = sample(lorem_contents, 2)
        for content in selected:
            suggestions.append(Suggestion(topic=topic, content=content))

    db.session.add_all(suggestions)
    db.session.commit()
    print("Seeding selesai.")
