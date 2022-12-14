from flask import Flask, render_template, url_for, request,redirect, make_response 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3

app = Flask(__name__)


def try_log():
    log = ''
    if request.cookies.get('login'):
        log = str(request.cookies.get('login'))
    return log 
        

@app.route('/')
@app.route('/home')
def index():
    log = try_log()
    return render_template('index.html',l_t = log)


@app.route('/reg',methods =  ['POST','GET'])
def reg():
    if request.method == 'POST':
        login = request.form['login']
        mail = request.form['mail']
        password = request.form['password']
        w_password = request.form['w_password']
        if password == w_password:
            try:
                conn = sqlite3.connect('fl5.db')
                cursor = conn.cursor()
                t_login = '''select * FROM users WHERE login = ?'''
                t_login  = cursor.execute(t_login, [login]).fetchall()
                t_password = '''select * FROM users WHERE login = ?'''
                t_password  = cursor.execute(t_password, [password]).fetchall()
                print(t_login)
                print(t_password)
                if len(t_login) != 0 :
                    conn.commit()
                    cursor.close()
                    return render_template('reg.html',text = 'этот логин  занят')
                elif len (t_password) != 0:
                    conn.commit()
                    cursor.close()
                    return render_template('reg.html',text = 'этот пароль занят')
                else:
                    users = '''INSERT INTO users (login,password,mail) VALUES(?,?,?)'''
                    cursor.execute(users, [login,generate_password_hash(password),mail])
                    conn.commit()
                    cursor.close()
                    res = make_response(redirect('/'))
                    res.set_cookie('login', login)
                    res.set_cookie('password', password)
                    return  res
            except Exception as e:
                print(e)
                return render_template('reg.html',text = 'что-то пошло не так..')
                
        else:
            return render_template('reg.html',text = 'неверный пароль')
            
    else:
        return render_template('reg.html')


@app.route('/input',methods =  ['POST','GET'])
def input():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        try:
            conn = sqlite3.connect('fl5.db')
            cursor = conn.cursor()
            d_password = '''select password FROM users WHERE login = ?'''
            d_password = cursor.execute(d_password, [login]).fetchall()[0][0]
            cursor.close()
            if check_password_hash(d_password, password):
                res = make_response(redirect('/'))
                res.set_cookie('login', login)
                res.set_cookie('password', password)
                return  res
            else:
                return render_template('input.html',text = 'вы ввели неверные данные')
        except Exception as e:
            print(e)
            return render_template('input.html',text = 'что-то пошло не так..')
            
    else:
        return render_template('input.html')


@app.route('/output')
def output():
    res = make_response(redirect('/'))
    res.set_cookie('login', '', max_age = 0)
    res.set_cookie('password','', max_age = 0)
    return res
    

@app.route('/creare_posts',methods =  ['POST','GET'])
def creare_posts():
    log = try_log()
    if log == '':
        print(1)
        return redirect ('/')
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        try:
            conn = sqlite3.connect('fl5.db')
            cursor = conn.cursor()
            pst = '''INSERT INTO pst (autor,title,intro,text,date) VALUES(?,?,?,?,?)'''
            cursor.execute(pst, [str(log),title,intro,text,datetime.now()])
            conn.commit()
            cursor.close()
            return redirect ('/post')
        except Exception as e:
            print(e)
            return render_template('creare_posts.html',text = 'что-то пошло не так.. ', l_t = log)
        return res
            
    else:
        return render_template('creare_posts.html', l_t = log)


@app.route('/post')
def all_post():
    log = try_log()
    conn = sqlite3.connect('fl5.db')
    cursor = conn.cursor()
    post = ''' SELECT * FROM pst ORDER BY date DESC '''
    post = cursor.execute(post).fetchall()
    conn.commit()
    cursor.close()
    return render_template('posts.html', post = post,l_t = log)


@app.route('/post/<int:t_id>',methods =  ['POST','GET'])
def posts_det(t_id):
    log = try_log()
    conn = sqlite3.connect('fl5.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        text = request.form['text']
        com = '''INSERT INTO com (p_id,autor,text,date) VALUES(?,?,?,?)'''
        cursor.execute('''INSERT INTO com (p_id,autor,text,date) VALUES(?,?,?,?)''', [t_id,log,text,datetime.now()])
        conn.commit()
        cursor.close()       
        return redirect('/post/'+str(t_id))
    else:
        text = ''' SELECT * FROM pst WHERE pst_id = ? '''
        text = cursor.execute(text,[t_id]).fetchall()[0]
        com = ''' SELECT * FROM com WHERE p_id = ? ORDER BY date DESC'''
        com = cursor.execute(com,[t_id]).fetchall()
        print(text)
        print(type(text[1]))
        conn.commit()
        cursor.close() 
        return render_template('post_det.html', text = text, com = com, l_t = log)

@app.route('/post/<int:t_id>/delete')
def posts_delete(t_id):
    conn = sqlite3.connect('fl5.db')
    cursor = conn.cursor()
    log = try_log()
    log_d = ''' SELECT autor FROM pst WHERE pst_id = ? '''
    log_d = cursor.execute(log_d,[t_id]).fetchall()[0][0]
    if log != log_d:
        return redirect('/')
    delete = ''' DELETE FROM pst WHERE pst_id =? '''
    delete = cursor.execute(delete,[t_id])
    delete = ''' DELETE FROM com WHERE p_id =? '''
    delete = cursor.execute(delete,[t_id])
    conn.commit()
    cursor.close()
    return redirect('/post')

@app.route('/post/<int:t_id>/update',methods =['POST','GET'])
def update(t_id):
    conn = sqlite3.connect('fl5.db')
    cursor = conn.cursor()
    log = try_log()
    log_d = ''' SELECT autor FROM pst WHERE pst_id = ? '''
    log_d = cursor.execute(log_d,[t_id]).fetchall()[0][0]
    if log != log_d:
        return redirect('/')
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        update =  """Update pst set title = ?, intro = ?, text = ?, date  = ?   where pst_id = ?  """
        update = cursor.execute(update,[title,intro,text,datetime.now(),t_id])
        conn.commit()
        cursor.close()
        return redirect('/post/'+ str(t_id))
      
    else:
        text = ''' SELECT * FROM pst  WHERE pst_id =? '''
        text = cursor.execute(text,[t_id]).fetchall()[0]
        conn.commit()
        cursor.close()
        return render_template('update.html', text = text, l_t = log)



@app.route('/post/<int:t_id>/com/<int:com_id>')
def posts_delete_com(t_id,com_id):
    conn = sqlite3.connect('fl5.db')
    cursor = conn.cursor()
    log = try_log()
    log_d = ''' SELECT autor FROM com WHERE c_id = ? '''
    log_d = cursor.execute(log_d,[com_id]).fetchall()[0][0]
    if log != log_d:
        return redirect('/')
    delete = ''' DELETE FROM com WHERE c_id =? '''
    delete = cursor.execute(delete,[com_id])
    conn.commit()
    cursor.close()
    return redirect('/post/'+str(t_id))

@app.route('/acnt/<user>')
def acnt (user):
    log = try_log()
    if log != user:
        return redirect('/')
    conn = sqlite3.connect('fl5.db')
    cursor = conn.cursor()
    us = ''' SELECT * FROM users WHERE login = ? '''
    us = cursor.execute(us,[user]).fetchall()[0]
    posts = ''' SELECT * FROM pst WHERE autor = ? ORDER BY date DESC '''
    posts = cursor.execute(posts,[user]).fetchall()
    cursor.close()
    print(posts)
    return render_template('acnt.html', l_t = log,us = us,posts = posts)


@app.route('/acnt/<user>/red',methods =  ['POST','GET'])
def acnt_red (user):
    log = try_log()
    if log != user:
        return redirect('/')
    if request.method == 'POST':
        password = request.form['password']
        try:
            conn = sqlite3.connect('fl5.db')
            cursor = conn.cursor()
            d_password = ''' SELECT password FROM users WHERE login = ? '''
            d_password = cursor.execute(d_password,[user]).fetchall()[0][0]
            cursor.close()
            if check_password_hash(d_password, password):
                return redirect('/acnt/'+user+'/red_t')        
            else:
                return render_template('acnt_red.html',text = 'вы ввели неверные данные', l_t = log)
        except Exception as e:
            print('err ',e)
            return render_template('acnt_red.html',text = 'что-то пошло не так..', l_t = log)
            
    else:
        return render_template('acnt_red.html', l_t = log)



@app.route('/acnt/<user>/red_t',methods =  ['POST','GET'])
def acnt_red_t (user):
    log = try_log()
    if log != user:
        return redirect('/')
    conn = sqlite3.connect('fl5.db')
    cursor = conn.cursor()
    us = ''' SELECT * FROM users WHERE login = ? '''
    us = cursor.execute(us,[user]).fetchall()[0]
    cursor.close()
    if request.method == 'POST':
        login = request.form['login']
        mail = request.form['mail']
        password = request.form['password']
        w_password = request.form['w_password']
        if password == w_password:
            try:
                conn = sqlite3.connect('fl5.db')
                cursor = conn.cursor()
                t_login = '''select * FROM users WHERE login = ?'''
                t_login  = cursor.execute(t_login, [login]).fetchall()
                t_password = '''select * FROM users WHERE login = ?'''
                t_password  = cursor.execute(t_password, [password]).fetchall()
                if len(t_login) != 0 :
                    if  t_login[0][1] !=  us[1]:
                        print(3)
                        conn.commit()
                        cursor.close()
                        return render_template('acnt_red_t.html',text = 'этот логин  занят', us = us,l_t = log)
                elif len (t_password) != 0 :
                    if  t_password[0][2] !=  us[2]:
                        conn.commit()
                        cursor.close()
                        return render_template('acnt_red_t.html',text = 'этот пароль занят', us = us,l_t = log)  
                res = make_response(redirect('/acnt/' + login))
                res.set_cookie('login', login)
                res.set_cookie('password', password)
                log = try_log()
                update =  """Update users set mail = ?, login = ?, password = ?   where login = ?  """
                update = cursor.execute(update,[mail,login,generate_password_hash(password),user])
                update =  """Update pst set autor = ? where autor = ? """
                update = cursor.execute(update,[login,user])
                update =  """Update com set autor = ? where autor = ? """
                update = cursor.execute(update,[login,user])
                conn.commit()
                cursor.close()
                return res
            except Exception as e:
                print(e)
                return render_template('acnt_red_t.html',text = 'что-то пошло не так..',us = us, l_t = log)
        else:
            return render_template('acnt_red_t.html',text = 'неверный пароль', l_t = log,us = us)

    else:
        return render_template('acnt_red_t.html',us = us, l_t = log)




if __name__ == "__main__":
    app.run()
    

