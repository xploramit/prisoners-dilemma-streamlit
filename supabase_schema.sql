create table if not exists public.game_state (
  id integer primary key,
  round_no integer not null default 1,
  match_index integer not null default 0,
  player_in_pair integer not null default 0,
  current_pairs jsonb not null default '[]'::jsonb,
  choices jsonb not null default '{}'::jsonb,
  scores jsonb not null default '{}'::jsonb,
  history jsonb not null default '[]'::jsonb,
  game_started boolean not null default false,
  game_finished boolean not null default false
);

insert into public.game_state (
  id, round_no, match_index, player_in_pair,
  current_pairs, choices, scores, history,
  game_started, game_finished
)
values (
  1, 1, 0, 0,
  '[]'::jsonb,
  '{}'::jsonb,
  '{"GUNGUN":0,"MAHIMA":0,"NGIPLO":0,"GODIVA":0,"LUHAMDI":0,"ZELLA":0,"ARSEY":0,"ROJITA":0,"BHARGAB":0,"RIJU":0}'::jsonb,
  '[]'::jsonb,
  false, false
)
on conflict (id) do nothing;
