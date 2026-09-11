# Future Enhancements

## Google Calendar
- [ ] Handle event conflicts (when an event exists in Google Calendar but not in local DB)
- [ ] Implement incremental sync (only sync changes since last sync) - currently we sync on every import
- [ ] Add sync interval scheduling (using APScheduler or similar)
- [ ] Improve error handling and reporting
- [ ] Support for multiple calendars (not just primary)
- [ ] Add ability to map lesson categories to Google Calendar colors or categories

## Obsidian Integration
- [ ] Implement Obsidian markdown export (as mentioned in the original design)
- [ ] Consider integrating with the Obsidian Google Calendar plugin if possible

## Scheduler
- [ ] Add APScheduler to run automated syncs at configurable times (e.g., 07:00 and 18:00)

## Statistics and Gamification
- [ ] Implement statistics engine (planned vs actual workload, charts)
- [ ] Add gamification layer (XP, levels, streaks, weekly review)

## Documentation
- [ ] Add more detailed architecture documentation
- [ ] Add API documentation (if we expand beyond health endpoint)
- [ ] Add user guide for end-users