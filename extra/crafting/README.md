# Installation
```toml
[[ballsdex.packages]]
path = "crafting"
enabled = true
```

# Crafting Package

Lets players combine two of their countryballs into a new one, following recipes
defined by administrators in the admin panel.

A `CraftRecipe` links two input balls to a result ball (and optionally a special).
Players run `/craft` with two of their countryballs; if a matching recipe exists
(in either order), the two inputs are soft-deleted and a new countryball is created
using the recipe's result ball and special. The new ball's attack and health bonuses
are picked at random between the two input balls' bonuses.

Note, for every new recipe added you do not need to restart the bot — recipes are
looked up live from the database.
