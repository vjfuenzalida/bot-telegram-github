drop table if exists chats;
create table chats (
  id integer primary key autoincrement,
  chat_id text not null
);
