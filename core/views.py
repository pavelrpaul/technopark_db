# encoding: utf-8
from utiles import ForumAnswer, ForumAnswerException, text_length, date_ok, limit_ok
from django.db import connection
from dateutil.parser import parse as check_date


def init_database():
    def execute(cursor, str):
        try:
            cursor.execute(str)
        except Exception as e:
            print e
    cursor = connection.cursor()
    
    execute(cursor, '''
        CREATE TABLE IF NOT EXISTS `Followers` (
            `followee` varchar({0}) NOT NULL,
            `follower` varchar({0}) NOT NULL,
            UNIQUE KEY `followee_follower` (`followee`,`follower`),
            KEY `followee` (`followee`),
            KEY `follower` (`follower`),
            INDEX `followee_index` (`followee` ASC)
        ) DEFAULT CHARSET=utf8;
    '''.format(text_length))
    execute(cursor, '''
        CREATE TABLE IF NOT EXISTS `Forums` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `name` varchar({0}) DEFAULT NULL,
            `short_name` varchar({0}) DEFAULT NULL,
            `user` varchar({0}) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `short_name_UNIQUE` (`short_name`),
            KEY `user` (`user`),
            UNIQUE INDEX `short_name_index` (`short_name` ASC),
            UNIQUE INDEX `id_index` (`id` ASC),
            INDEX `user_index` (`user` ASC)
        ) AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
    '''.format(text_length))
    execute(cursor, '''
        CREATE TABLE IF NOT EXISTS `Posts` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `message` text,
            `date` timestamp NULL DEFAULT NULL,
            `likes` int(11) DEFAULT '0',
            `dislikes` int(11) DEFAULT '0',
            `points` int(11) DEFAULT '0',
            `isApproved` tinyint(4) DEFAULT NULL,
            `isHighlighted` tinyint(4) DEFAULT NULL,
            `isEdited` tinyint(4) DEFAULT NULL,
            `isSpam` tinyint(4) DEFAULT NULL,
            `isDeleted` tinyint(4) DEFAULT NULL,
            `parent` int(11) DEFAULT NULL,
            `user` varchar({0}) NOT NULL,
            `thread` int(11) NOT NULL,
            `forum` varchar({0}) NOT NULL,
            PRIMARY KEY (`id`),
            KEY `user` (`user`),
            KEY `thread` (`thread`),
            KEY `forum` (`forum`),
            INDEX `user_index` (`user` ASC),
            INDEX `thread_index` (`thread` ASC),
            INDEX `parent_index` (`parent` ASC),
            INDEX `forum_index` (`forum` ASC)
        ) AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
    '''.format(text_length))
    execute(cursor, '''
        CREATE TABLE IF NOT EXISTS `Subscriptions` (
            `thread` int(11) NOT NULL,
            `user` varchar({0}) NOT NULL,
            UNIQUE KEY `user_email_threads_id` (`thread`,`user`),
            KEY `user` (`user`),
            KEY `thread` (`thread`),
            INDEX `thread_index` (`thread` ASC),
            INDEX `user_index` (`user` ASC)
        ) DEFAULT CHARSET=utf8;
    '''.format(text_length))
    execute(cursor, '''
        CREATE TABLE IF NOT EXISTS `Threads` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `title` varchar({0}) DEFAULT NULL,
            `slug` varchar({0}) DEFAULT NULL,
            `message` text,
            `date` timestamp NULL DEFAULT NULL,
            `likes` int(11) DEFAULT '0',
            `dislikes` int(11) DEFAULT '0',
            `points` int(11) DEFAULT '0',
            `isClosed` tinyint(4) DEFAULT NULL,
            `isDeleted` tinyint(4) DEFAULT NULL,
            `posts` int(11) DEFAULT '0',
            `forum` varchar({0}) NOT NULL,
            `user` varchar({0}) NOT NULL,
            PRIMARY KEY (`id`),
            KEY `forum` (`forum`),
            KEY `user` (`user`),
            UNIQUE INDEX `id_index` (`id` ASC),
            INDEX `user_index` (`user` ASC),
            INDEX `forum_index` (`forum` ASC)
        ) AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
    '''.format(text_length))
    execute(cursor, '''
        CREATE TABLE IF NOT EXISTS `Users` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `username` varchar({0}) DEFAULT NULL,
            `about` text,
            `name` varchar({0}) DEFAULT NULL,
            `email` varchar({0}) DEFAULT NULL,
            `isAnonymous` tinyint(4) DEFAULT '0',
            PRIMARY KEY (`id`),
            UNIQUE KEY `email` (`email`),
            UNIQUE INDEX `email_index` (`email` ASC),
            UNIQUE INDEX `id_index` (`id` ASC)
        ) AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
    '''.format(text_length))


def test(request):
    from django.http import HttpResponse
    from os import system

    system('''
        cd database/tests/tests/
        python func_test.py -l --address=127.0.0.1:8000
    ''')

    return HttpResponse('ok')


class ForumBase(ForumAnswer):

    def forum_description(self, forum):
        forum = forum[0]
        return {
            'id': forum[0],
            'name': forum[1],
            'short_name': forum[2],
            'user': forum[3]
        }

    def forum_details(self, cursor, short_name, related):
        forum = cursor.select('''
            SELECT id, name, short_name, user FROM Forums WHERE short_name = %s
        ''', (short_name,))

        if len(forum) == 0:
            return {'code': 1, 'response': 'forum with short_name {0} not found'.format(short_name)}
        forum = self.forum_description(forum)

        if 'user' in related:
            forum['user'] = self.user_details(cursor, forum['user'])
        return forum


class UserBase(ForumAnswer):

    def user_format(self, user):
        user = user[0]
        return {
            'about': user[1],
            'email': user[0],
            'id': user[3],
            'isAnonymous': bool(user[2]),
            'name': user[4],
            'username': user[5]
        }

    def user_details(self, cursor, email):
        user = cursor.select('''
            SELECT email, about, isAnonymous, id, name, username FROM Users WHERE email = %s
        ''', (email,))

        if len(user) == 0:
            return {'code': 1, 'response': 'No user with email ' + email}
        user = self.user_format(user)

        user['followers'] = self.to_list(cursor.select('''
            SELECT follower FROM Followers JOIN Users ON Users.email = Followers.follower
            WHERE followee = %s
        ''', (email,)))

        user['following'] = self.to_list(cursor.select('''
            SELECT followee FROM Followers JOIN Users ON Users.email = Followers.followee
            WHERE follower = %s
        ''', (email,)))

        user['subscriptions'] = self.to_list(cursor.select('''
            SELECT thread FROM Subscriptions WHERE user = %s
        ''', (email,)))

        return user

    def to_list(self, tup):
        r = []
        for el in tup:
            r.append(el[0])
        return r

    def followers(self, data, cursor, select_what, select_where):
        email = data['user']
        cursor.exists('Users', 'email', email)

        query = '''
            SELECT {0} FROM Followers JOIN Users ON Users.email = Followers.{0}
            WHERE {1} = %s 
        '''.format(select_what, select_where)

        try:
            since_id = int(data.get('since_id'))
            if since_id >= 0:
                query += ' AND Users.id >= {0} '.format(str(since_id))
        except (ValueError, TypeError):
            pass

        if data.get('order') == 'asc':
            query += ' ORDER BY Users.name ASC '
        else:
            query += ' ORDER BY Users.name DESC '
        
        limit = data.get('limit')
        if limit_ok(limit):
            query += ' LIMIT {0} '.format(limit)

        followers_tuple = cursor.select(query, (email,))

        followers = []
        for follower in followers_tuple:
            followers.append(self.user_details(cursor, follower[0]))

        return followers


class ThreadBase(UserBase, ForumBase):

    def thread_close(self, cursor, id, isClosed):
        cursor.exists('Threads', 'id', id)
        cursor.execute('''
            UPDATE Threads SET isClosed = %s WHERE id = %s
        ''', (isClosed, id,))

        return {
            'thread': id
        }

    def thread_details(self, cursor, id, related):
        thread = cursor.select('''
            SELECT date, forum, id, isClosed, isDeleted, message, slug, title, user, dislikes, likes, points, posts
            FROM Threads WHERE id = %s
        ''', (id,))

        if len(thread) == 0:
            raise ForumAnswerException('Thread {0} does not exist'.format(str(id)))

        posts = cursor.select('''
            SELECT COUNT(id) FROM Posts WHERE thread = %s AND isDeleted = 0
        ''', (id,))[0][0]
        
        thread = thread[0]
        thread = {
            'date': str(thread[0]),
            'forum': thread[1],
            'id': thread[2],
            'isClosed': bool(thread[3]),
            'isDeleted': bool(thread[4]),
            'message': thread[5],
            'slug': thread[6],
            'title': thread[7],
            'user': thread[8],
            'dislikes': thread[9],
            'likes': thread[10],
            'points': thread[11],
            'posts': posts,
        }

        if 'user' in related:
            thread['user'] = self.user_details(cursor, thread['user'])
        if 'forum' in related:
            thread['forum'] = self.forum_details(cursor, thread['forum'], [])

        return thread

    def thread_remove(self, cursor, id, isDeleted):
        cursor.exists('Threads', 'id', id)
        cursor.execute('''
            UPDATE Threads SET isDeleted = %s WHERE id = %s
        ''', (isDeleted, id,))

        if isDeleted:
            cursor.execute('''
                UPDATE Posts SET isDeleted = 2 WHERE thread = %s AND isDeleted = 0
            ''', (id,))
        else:
            cursor.execute('''
                UPDATE Posts SET isDeleted = 0 WHERE thread = %s AND isDeleted = 2
            ''', (id,))

        return {
            'thread': id
        }


class PostBase(ThreadBase):
    def post_formated(self, post):
        post = post[0]
        return {
            'date': str(post[0]),
            'dislikes': post[1],
            'forum': post[2],
            'id': post[3],
            'isApproved': bool(post[4]),
            'isDeleted': bool(post[5]),
            'isEdited': bool(post[6]),
            'isHighlighted': bool(post[7]),
            'isSpam': bool(post[8]),
            'likes': post[9],
            'message': post[10],
            'parent': post[11],
            'points': post[12],
            'thread': post[13],
            'user': post[14],
        }

    def post_details(self, cursor, id, related):
        post = cursor.select('''
            SELECT date, dislikes, forum, id, isApproved, isDeleted, isEdited,
            isHighlighted, isSpam, likes, message, parent, points, thread, user
            FROM Posts WHERE id = %s
        ''', (id,))

        if len(post) == 0:
            raise ForumAnswerException('post {0} does not exist'.format(id))

        post = self.post_formated(post)

        if 'user' in related:
            post['user'] = self.user_details(cursor, post['user'])
        if 'forum' in related:
            post['forum'] = self.forum_details(cursor, post['forum'], [])
        if 'thread' in related:
            post['thread'] = self.thread_details(cursor, post['thread'], [])

        return post

    def post_remove(self, cursor, id, isDeleted):
        cursor.exists('Posts', 'id', id)
        cursor.execute('''
            UPDATE Posts SET isDeleted = %s WHERE Posts.id = %s
        ''', (isDeleted, id,))
        return {
            'post': id
        }

    def post_list(self, cursor, data):
        forum = data.get('forum')
        thread = data.get('thread')
        user = data.get('user')

        if forum:
            cursor.exists('Forums', 'short_name', forum)
            query = 'SELECT id FROM Posts WHERE forum = %s '
            params = [forum]
        elif thread:
            cursor.exists('Threads', 'id', thread)
            query = 'SELECT id FROM Posts WHERE thread = %s '
            params = [thread]
        elif user:
            cursor.exists('Users', 'email', user)
            query = 'SELECT id FROM Posts WHERE user = %s '
            params = [user]

        since = data.get('since')
        if date_ok(since):
            query += ' AND date >= %s '
            params.append(since)
        
        if data.get('order') == 'asc':
            query += ' ORDER BY date ASC '
        else:
            query += ' ORDER BY date DESC '
        
        limit = data.get('limit')
        if limit_ok(limit):
            query += ' LIMIT {0} '.format(limit)

        related = data.get('related', [])
        ids = cursor.select(query, params)
        posts = []
        for id in ids:
            posts.append(self.post_details(cursor, id[0], related))

        return posts


class Clear(ForumAnswer):
    methods = ['post']

    def on(self, data, cursor):
        cursor.execute('DROP TABLE Followers;')
        cursor.execute('DROP TABLE Forums;')
        cursor.execute('DROP TABLE Posts;')
        cursor.execute('DROP TABLE Subscriptions;')
        cursor.execute('DROP TABLE Threads;')
        cursor.execute('DROP TABLE Users;')
        
        init_database()
        
        return {'code': 0, 'response': 'OK'}


class Status(ForumAnswer):
    methods = ['get']

    def on(self, data, cursor):
        info = cursor.select('''
            SELECT count(id) FROM Users
            UNION ALL
            SELECT count(id) FROM Threads
            UNION ALL
            SELECT count(id) FROM Forums
            UNION ALL
            SELECT count(id) FROM Posts;
        ''')
        response = {
            'user': info[0][0],
            'thread': info[1][0],
            'forum': info[2][0],
            'post': info[3][0]
        }
        return {'code': 0, 'response': response}


class ForumCreate(ForumBase):
    methods = ['post']
    reqired_parameters = ['name', 'short_name', 'user']

    def on(self, data, cursor):
        name = data['name']
        user = data['user']
        short_name = data['short_name']

        cursor.exists('Users', 'email', user)
        forum = cursor.select('''
            select id, name, short_name, user FROM Forums WHERE short_name = %s
        ''', (short_name,))

        if len(forum) == 0:
            cursor.execute('''
                INSERT INTO Forums (name, short_name, user) VALUES (%s, %s, %s)
            ''', (name, short_name, user,))
            forum = cursor.select('''
                select id, name, short_name, user FROM Forums WHERE short_name = %s
            ''', (short_name,))

        return {'code': 0, 'response': self.forum_description(forum)}


class ForumDetails(ForumBase, UserBase):
    methods = ['get']
    optional_get_arrays = ['related']
    reqired_parameters = ['forum']

    def on(self, data, cursor):
        short_name = data['forum']
        related = data.get('related', [])
        forum = self.forum_details(cursor, short_name, related)
        return {'code': 0, 'response': forum}


class ForumListThreads(ThreadBase):
    methods = ['get']
    optional_get_arrays = ['related']
    reqired_parameters = ['forum']

    def on(self, data, cursor):
        forum = data['forum']
        related = data.get('related', [])

        cursor.exists('Forums', 'short_name', forum)
        query = 'SELECT id FROM Threads WHERE forum = %s '
        params = [forum]

        since = data.get('since')
        if date_ok(since):
            query += ' AND date >= %s '
            params.append(since)
        
        if data.get('order') == 'asc':
            query += ' ORDER BY date ASC '
        else:
            query += ' ORDER BY date DESC '
        
        limit = data.get('limit')
        if limit_ok(limit):
            query += ' LIMIT {0} '.format(limit)

        thread_ids = cursor.select(query, params)
        
        threads = []
        for id in thread_ids:
            threads.append(self.thread_details(cursor, id[0], related))

        return {'code': 0, 'response': threads}


class ForumListPosts(PostBase):
    methods = ['get']
    optional_get_arrays = ['related']
    reqired_parameters = ['forum']

    def on(self, data, cursor):
        data['thread'] = None
        data['user'] = None

        response = self.post_list(cursor, data)

        return {'code': 0, 'response': response}


class ForumListUsers(ForumBase, UserBase):
    methods = ['get']
    reqired_parameters = ['forum']

    def on(self, data, cursor):
        short_name = data['forum']

        cursor.exists('Forums', 'short_name', short_name)

        query = '''
            SELECT distinct email FROM Users JOIN Posts ON Posts.user = Users.email 
            JOIN Forums on Forums.short_name = Posts.forum WHERE Posts.forum = %s
        '''
        
        try:
            since_id = int(data.get('since_id'))
            if since_id >= 0:
                query += ' AND Users.id >= {0} '.format(str(since_id))
        except (ValueError, TypeError):
            pass

        if data.get('order') == 'asc':
            query += ' ORDER BY Users.name ASC '
        else:
            query += ' ORDER BY Users.name DESC '

        limit = data.get('limit')
        if limit_ok(limit):
            query += ' LIMIT {0} '.format(limit)

        users_tuple = cursor.select(query, (short_name,))
        
        users = []
        for user in users_tuple:
            users.append(self.user_details(cursor, user[0]))

        return {'code': 0, 'response': users}


class PostCreate(PostBase):
    methods = ['post']
    long_texts = ['message']
    reqired_parameters = ['date', 'thread:int', 'message', 'user', 'forum']

    def on(self, data, cursor):
        date = data['date']
        thread = data['thread']
        message = data['message']
        user = data['user']
        forum = data['forum']
        #
        # if not date_ok(date):
        #     return {'code': 1, 'response': 'Bad date'}
        #
        # cursor.exists('Threads', 'id', thread)
        # cursor.exists('Forums', 'short_name', forum)
        # cursor.exists('Users', 'email', user)
        #
        # if len(cursor.select('''
        #     SELECT Threads.id FROM Threads JOIN Forums ON Threads.forum = Forums.short_name
        #     WHERE Threads.forum = %s AND Threads.id = %s
        # ''', (forum, thread,) )) == 0:
        #     return {'code': 1, 'response': 'thread {0} does not exist in forum {1}'.format(str(thread), forum) }
        #
        # if 'parent' in data:
        #     if data['parent'] is not None and len(cursor.select('''
        #         SELECT Posts.id FROM Posts JOIN Threads ON Threads.id = Posts.thread
        #         WHERE Posts.id = %s AND Threads.id = %s
        #     ''', (data['parent'], thread,) )) == 0:
        #         return {'code': 1, 'response': 'Post {0} does not exist'.format(data['parent']) }
        #
        query = 'INSERT INTO Posts (message, user, forum, thread, date'
        values = '(%s, %s, %s, %s, %s'
        parameters = [message, user, forum, thread, date]

        optional = ['parent', 'isApproved', 'isHighlighted', 'isEdited', 'isSpam', 'isDeleted']
        for param in data:
            if param in optional and (param == 'parent' or type(data[param]) is bool):
                query += ', ' + param
                values += ', %s'
                parameters.append(data[param])

        query += ') VALUES ' + values + ')'

        update_thread_posts = 'UPDATE Threads SET posts = posts + 1 WHERE id = %s'

        cursor.execute(update_thread_posts, (thread,))
        post_id = cursor.execute(query, parameters)[0]

        post = cursor.select('''
            SELECT date, forum, id, isApproved, isDeleted, isEdited, isHighlighted,
            isSpam, message, parent, thread, user
            FROM Posts WHERE id = %s
        ''', (post_id,))

        post = post[0]
        response = {
            'date': str(post[0]),
            'forum': post[1],
            'id': post[2],
            'isApproved': bool(post[3]),
            'isDeleted': bool(post[4]),
            'isEdited': bool(post[5]),
            'isHighlighted': bool(post[6]),
            'isSpam': bool(post[7]),
            'message': post[8],
            'parent': post[9],
            'thread': post[10],
            'user': post[11]
        }

        return {'code': 0, 'response': response}


class PostDetails(PostBase, ThreadBase):
    methods = ['get']
    optional_get_arrays = ['related']
    reqired_parameters = ['post:int']

    def on(self, data, cursor):
        id = data['post']
        related = data.get('related', [])

        response = self.post_details(cursor, id, related)

        return {'code': 0, 'response': response}


class PostList(PostBase):
    methods = ['get']
    reqired_parameters = ['forum|thread:int']

    def on(self, data, cursor):
        data['user'] = None

        response = self.post_list(cursor, data)

        return {'code': 0, 'response': response}


class PostRemove(PostBase):
    methods = ['post']
    reqired_parameters = ['post:int']

    def on(self, data, cursor):
        id = data['post']
        isDeleted = True

        response = self.post_remove(cursor, id, isDeleted)

        return {'code': 0, 'response': response}


class PostRestore(PostBase):
    methods = ['post']
    reqired_parameters = ['post:int']

    def on(self, data, cursor):
        id = data['post']
        isDeleted = False

        response = self.post_remove(cursor, id, isDeleted)

        return {'code': 0, 'response': response}


class PostUpdate(PostBase):
    methods = ['post']
    reqired_parameters = ['post:int', 'message']

    def on(self, data, cursor):
        id = data['post']
        message = data['message']

        cursor.exists('Posts', 'id', id)
        cursor.execute('''
            UPDATE Posts SET message = %s WHERE id = %s
        ''', (message, id,))
        response = self.post_details(cursor, id, [])

        return {'code': 0, 'response': response}


class PostVote(PostBase):
    methods = ['post']
    reqired_parameters = ['vote:int', 'post:int']

    def on(self, data, cursor):
        vote = data['vote']
        id = data['post']

        cursor.exists('Posts', 'id', id)

        if vote == -1:
            cursor.execute('''
                UPDATE Posts SET dislikes=dislikes+1, points=points-1 where id = %s
            ''', (id,))
        elif vote == 1:
            cursor.execute('''
                UPDATE Posts SET likes=likes+1, points=points+1  where id = %s
            ''', (id,))

        response = self.post_details(cursor, id, [])
        
        return {'code': 0, 'response': response}


class UserCreate(UserBase):
    methods = ['post']
    long_texts = ['about']
    reqired_parameters = ['username', 'about', 'name', 'email']

    def on(self, data, cursor):
        isAnonymous = data.get('isAnonymous', 0)
        username = data['username']
        about = data['about']
        name = data['name']
        email = data['email']
        
        user = cursor.select('''
            SELECT email, about, isAnonymous, id, name, username FROM Users WHERE email = %s
        ''', (email,))

        if len(user) == 0:
            cursor.execute('''
                INSERT INTO Users (email, about, name, username, isAnonymous) VALUES (%s, %s, %s, %s, %s)
            ''', (email, about, name, username, isAnonymous,))

            user = cursor.select('''
                SELECT email, about, isAnonymous, id, name, username FROM Users WHERE email = %s
            ''', (email,))

            return {'code': 0, 'response': self.user_format(user)}
        
        return {'code': 5, 'response': 'User already exists'}


class UserDetails(UserBase):
    methods = ['get']
    reqired_parameters = ['user']

    def on(self, data, cursor):
        email = data['user']

        user = self.user_details(cursor, email)

        return {'code': 0, 'response': user}


class UserFollow(UserBase):
    methods = ['post']
    reqired_parameters = ['follower', 'followee']

    def on(self, data, cursor):
        follower = data['follower']
        followee = data['followee']

        cursor.exists('Users', 'email', follower)
        cursor.exists('Users', 'email', followee)

        if follower == followee:
            return {'code': 1, 'response': 'Emails are the same'}

        follows = cursor.select('''
            SELECT follower FROM Followers WHERE follower = %s AND followee = %s
        ''', (follower, followee,))

        if len(follows) == 0:
            cursor.execute('''
                INSERT INTO Followers (follower, followee) VALUES (%s, %s)
            ''', (follower, followee,))

        return {'code': 0, 'response': self.user_details(cursor, follower)}


class UserUnfollow(UserBase):
    methods = ['post']
    reqired_parameters = ['follower', 'followee']

    def on(self, data, cursor):
        follower = data['follower']
        followee = data['followee']

        follows = cursor.select('''
            SELECT follower FROM Followers WHERE follower = %s AND followee = %s
        ''', (follower, followee,))

        if len(follows) == 0:
            return {'code': 0, 'response': 'No following found'}

        cursor.execute('''
            DELETE FROM Followers WHERE follower = %s AND followee = %s
        ''', (follower, followee,))
        
        return {'code': 0, 'response': self.user_details(cursor, follower)}


class UserListFollowers(UserBase):
    methods = ['get']
    reqired_parameters = ['user']

    def on(self, data, cursor):
        followers = self.followers(data, cursor, 'follower', 'followee')
        return {'code': 0, 'response': followers}


class UserListFollowing(UserBase):
    methods = ['get']
    reqired_parameters = ['user']

    def on(self, data, cursor):
        followers = self.followers(data, cursor, 'followee', 'follower')
        return {'code': 0, 'response': followers}


class UserUpdateProfile(UserBase):
    methods = ['post']
    reqired_parameters = ['about', 'user', 'name']

    def on(self, data, cursor):
        about = data['about']
        email = data['user']
        name = data['name']

        cursor.exists('Users', 'email', email)
        cursor.execute('''
            UPDATE Users SET email = %s, about = %s, name = %s WHERE email = %s
        ''', (email, about, name, email,))

        return {'code': 0, 'response': self.user_details(cursor, email)}


class UserListPosts(PostBase):
    methods = ['get']
    optional_get_arrays = ['related']
    reqired_parameters = ['user']

    def on(self, data, cursor):
        data['thread'] = None
        data['forum'] = None

        response = self.post_list(cursor, data)

        return {'code': 0, 'response': response}


class ThreadCreate(ThreadBase):
    methods = ['post']
    long_texts = ['message']
    reqired_parameters = ['forum', 'title', 'isClosed:bool', 'user', 'date', 'message', 'slug']

    def on(self, data, cursor):
        forum = data['forum']
        title = data['title']
        isClosed = data['isClosed']
        user = data['user']
        date = data['date']
        message = data['message']
        slug = data['slug']
        isDeleted = data.get('isDeleted', 0)

        if not date_ok(date):
            return {'code': 1, 'response': 'Bad date'}

        cursor.exists('Users', 'email', user)
        cursor.exists('Forums', 'short_name', forum)

        thread = cursor.select('''
            SELECT date, forum, id, isClosed, isDeleted, message, slug, title, user, dislikes, likes, points, posts 
            FROM Threads WHERE slug = %s
            ''', (slug,))
        if len(thread) == 0:
            cursor.execute('''
                INSERT INTO Threads (forum, title, isClosed, user, date, message, slug, isDeleted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (forum, title, isClosed, user, date, message, slug, isDeleted,))
            thread = cursor.select('''
                SELECT date, forum, id, isClosed, isDeleted, message, slug, title, user
                FROM Threads WHERE slug = %s
            ''', (slug,))

        thread = thread[0]
        response = {
            'date': str(thread[0]),
            'forum': thread[1],
            'id': thread[2],
            'isClosed': bool(thread[3]),
            'isDeleted': bool(thread[4]),
            'message': thread[5],
            'slug': thread[6],
            'title': thread[7],
            'user': thread[8],
        }

        return {'code': 0, 'response': response}


class ThreadDetails(ThreadBase, UserBase, ForumBase):
    methods = ['get']
    optional_get_arrays = ['related']
    reqired_parameters = ['thread:int']

    def on(self, data, cursor):
        id = data['thread']

        thread = cursor.select('''
            SELECT date, forum, id, isClosed, isDeleted, message, slug, title, user, dislikes, likes, points, posts 
            FROM Threads WHERE id = %s
        ''', (id,))

        if len(thread) == 0:
            return {'code': 1, 'response': 'No thread exists with id {0}'.format(str(id))}

        posts = cursor.select('''
            SELECT COUNT(id) FROM Posts WHERE thread = %s AND isDeleted = 0
        ''', (id,))[0][0]

        thread = thread[0]
        thread = {
            'date': str(thread[0]),
            'forum': thread[1],
            'id': thread[2],
            'isClosed': bool(thread[3]),
            'isDeleted': bool(thread[4]),
            'message': thread[5],
            'slug': thread[6],
            'title': thread[7],
            'user': thread[8],
            'dislikes': thread[9],
            'likes': thread[10],
            'points': thread[11],
            'posts': posts,
        }

        related = data.get('related', [])
        if 'user' in related:
            thread['user'] = self.user_details(cursor, thread['user'])
        if 'forum' in related:
             thread['forum'] = self.forum_details(cursor, thread['forum'], [])
        if 'thread' in related:
            return {'code': 3, 'response': 'blablabla'}

        return {'code': 0, 'response': thread}


class ThreadSubscribe(ThreadBase):
    methods = ['post']
    reqired_parameters = ['user', 'thread:int']

    def on(self, data, cursor):
        id = data['thread']
        email = data['user']

        cursor.exists('Threads', 'id', id)
        cursor.exists('Users', 'email', email)

        subscription = cursor.select('''
            SELECT thread, user FROM Subscriptions WHERE user = %s AND thread = %s
        ''', (email, id,))

        if len(subscription) == 0:
            cursor.execute('''
                INSERT INTO Subscriptions (thread, user) VALUES (%s, %s)
            ''', (id, email,))

            subscription = cursor.select('''
                SELECT thread, user FROM Subscriptions WHERE user = %s AND thread = %s
            ''', (email, id,))

        subscription = subscription[0]
        response = {
            'thread': subscription[0],
            'user': subscription[1]
        }

        return {'code': 0, 'response': response}


class ThreadUnsubscribe(ThreadBase):
    methods = ['post']
    reqired_parameters = ['user', 'thread:int']

    def on(self, data, cursor):
        id = data['thread']
        email = data['user']

        cursor.exists('Threads', 'id', id)
        cursor.exists('Users', 'email', email)
        
        subscription = cursor.select('''
            SELECT thread, user FROM Subscriptions WHERE user = %s AND thread = %s'''
        ,(email, id, ))

        if len(subscription) == 0:
            return {'code': 1, 'response': '{0} is not part of thread {1}'.format(email, str(id))}
        
        cursor.execute('''
            DELETE FROM Subscriptions WHERE user = %s AND thread = %s
        ''', (email, id,))

        subscription = subscription[0]
        response = {
            'thread': subscription[0],
            'user': subscription[1]
        }

        return {'code': 0, 'response': response}


class ThreadOpen(ThreadBase):
    methods = ['post']
    reqired_parameters = ['thread:int']

    def on(self, data, cursor):
        id = data['thread']
        isClosed = False

        response = self.thread_close(cursor, id, isClosed)
        return {'code': 0, 'response': response}


class ThreadClose(ThreadBase):
    methods = ['post']
    reqired_parameters = ['thread:int']

    def on(self, data, cursor):
        id = data['thread']
        isClosed = True

        response = self.thread_close(cursor, id, isClosed)
        return {'code': 0, 'response': response}


class ThreadVote(ThreadBase):
    methods = ['post']
    reqired_parameters = ['vote:int', 'thread:int']

    def on(self, data, cursor):
        id = data['thread']
        vote = data['vote']

        cursor.exists('Threads', 'id', id)

        if vote == -1:
            cursor.execute('''
                UPDATE Threads SET dislikes=dislikes+1, points=points-1 where id = %s
            ''', (id,))
        elif vote == 1:
            cursor.execute('''
                UPDATE Threads SET likes=likes+1, points=points+1  where id = %s
            ''', (id,))

        response = self.thread_details(cursor, id, [])
        return {'code': 0, 'response': response}


class ThreadList(ThreadBase):
    methods = ['get']
    reqired_parameters = ['user|forum']

    def on(self, data, cursor):
        user  = data.get('user')
        forum = data.get('forum')

        if user:
            cursor.exists('Users', 'email', user)
            query = 'SELECT id FROM Threads WHERE user = %s '
            params = [user]
        else:
            cursor.exists('Forums', 'short_name', forum)
            query = 'SELECT id FROM Threads WHERE forum = %s '
            params = [forum]

        since = data.get('since')
        if date_ok(since):
            query += ' AND date >= %s '
            params.append(since)

        if data.get('order')  == 'asc':
            query += ' ORDER BY date ASC '
        else:
            query += ' ORDER BY date DESC '
        
        limit = data.get('limit_ok')
        if limit_ok(limit):
            query += ' LIMIT {0} '.format(limit)

        thread_ids = cursor.select(query, params)
        
        threads = []
        for id in thread_ids:
            threads.append(self.thread_details(cursor, id[0], []))

        return {'code': 0, 'response': threads}


class ThreadUpdate(ThreadBase):
    methods = ['post']
    long_texts = ['message']
    reqired_parameters = ['message', 'slug', 'thread:int']

    def on(self, data, cursor):
        message = data['message']
        slug    = data['slug']
        id      = data['thread']

        cursor.exists('Threads', 'id', id)
        cursor.execute('''
            UPDATE Threads SET slug = %s, message = %s WHERE id = %s
        ''', (slug, message, id,))

        response = self.thread_details(cursor, id, [])
        return {'code': 0, 'response': response}


class ThreadRemove(ThreadBase):
    methods = ['post']
    reqired_parameters = ['thread:int']

    def on(self, data, cursor):
        id = data['thread']
        isDeleted = True

        response = self.thread_remove(cursor, id, isDeleted)
        return {'code': 0, 'response': response}


class ThreadRestore(ThreadBase):
    methods = ['post']
    reqired_parameters = ['thread:int']

    def on(self, data, cursor):
        id = data['thread']
        isDeleted = False

        response = self.thread_remove(cursor, id, isDeleted)
        return {'code': 0, 'response': response}


class ThreadListPosts(PostBase):
    methods = ['get']
    optional_get_arrays = ['related']
    reqired_parameters = ['thread:int']

    def on(self, data, cursor):
        data['forum'] = None
        data['user']  = None

        response = self.post_list(cursor, data)

        return {'code': 0, 'response': response}

