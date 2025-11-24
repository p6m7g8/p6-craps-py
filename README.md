# P6's POSIX.2: p6-template-pipenv

## Table of Contents

## Badges

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![Mergify](https://img.shields.io/endpoint.svg?url=https://gh.mergify.io/badges//p6-template-pipenv/&style=flat)](https://mergify.io)
[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](<https://gitpod.io/#https://github.com//p6-template-pipenv>)

## Summary

## Contributing

- [How to Contribute](<https://github.com//.github/blob/main/CONTRIBUTING.md>)

## Code of Conduct

- [Code of Conduct](<https://github.com//.github/blob/main/CODE_OF_CONDUCT.md>)

## Modules

```text

                                       players
config.json -> config.py -> sim.py ->  strategy
                                       engine    -> stats -> ui/terminal -> bin/script -> bin/ctl

```

```text
1. CLI startup (bin/script.py)
------------------------------

bin/script.py
  |
  |-- parse args with docopt:
  |     --config, --max-rolls, --frame-delay, --no-clear, --debug/--verbose
  |
  |-- setup_logging(...)
  |
  |-- cfg = load_config(path)          (config.Config)
  |-- sim = Simulation(cfg)            (sim.Simulation)
  |      |
  |      +-> create_player_states(cfg) (players.PlayerState[])
  |      +-> get_strategy_by_name(...) (strategy.*)
  |      +-> CrapsEngine(), CrapsTable() (engine.*)
  |
  |-- result = sim.run(max_rolls, frame_callback)
  |
  |-- summary = summarize_simulation(sim.players, result) (stats.SimulationSummary)
  |
  |-- final UI:
  |     - live frames already drawn via frame_callback
  |     - format_summary(summary) + print


2. Inside Simulation.run(...)
-----------------------------

for each run:

  initial:
    - maybe call frame_callback(sim, None, "initial")

  loop:
    while no stop_reason and max_rolls not hit:

      a) start new roll
         - self._roll_index        += 1
         - self._shooter_roll_index+= 1

      b) betting phase
         for each (player_index, (player_state, strategy)):

             if player outside bankroll limits: skip

             game_state = {
               GAME_STATE_PHASE:          engine.phase,
               GAME_STATE_HAS_PASS_LINE_BET:
                                         table.has_pass_line_bet(player_index),
             }

             decisions = strategy.decide(game_state, player_state)
             _apply_bet_decisions(decisions, ...)
               -> PlayerState.debit(...)
               -> CrapsTable.place_bet(Bet(...))

         frame_callback(sim, None, "after_bets")

      c) roll dice
         point_cycle = engine.roll()          (engine.CrapsEngine.roll)
         temp_event  = SimulationEvent(..., resolved_bets=())
         frame_callback(sim, temp_event, "after_roll")

      d) resolve bets
         resolved = table.resolve_on_point_cycle_result(point_cycle)
           -> produces ResolvedBet objects keyed by Bet/player

         for each resolved:
             if resolved.payout > 0:
                 PlayerState.credit(resolved.payout)

         if point_cycle.completed_point:
             players[current_shooter].points_played_as_shooter += 1
             _advance_shooter()

         final_event = SimulationEvent(..., resolved_bets=resolved)
         events.append(final_event)

         frame_callback(sim, final_event, "after_payouts")

      e) check stop conditions
         stop_reason = _should_stop()
           - STOP_REASON_MAX_POINTS if engine.completed_points >= cfg.simulation.points
           - STOP_REASON_BANKROLL   if all players at bankroll limits
           - or STOP_REASON_MAX_ROLLS if max_rolls guard trips

  return SimulationResult(events, completed_points, stop_reason)


3. What the UI & stats see
--------------------------

- During the run:
    frame_callback(sim, event, stage) in bin/script.py:

      - build_header_info(sim.engine, roll_index, shooter_index, shooter_roll_index)
      - snapshot_players(sim.players, sim.table)
      - render_frame(header, player_rows)
      - draw_frame(stdout, frame, clear=not --no-clear)
      - optional time.sleep(--frame-delay)

- After the run:
    summary = summarize_simulation(sim.players, result):

      - compute_dice_totals(result.events)
      - summarize_players(sim.players)
      - SimulationSummary(stop_reason, completed_points, dice_stats, player_summaries)

    ui.terminal.format_summary(summary) turns that into a text block
    printed under the final live frame.
```

## Author

Philip M . Gollucci <pgollucci@p6m7g8.com>
