import streamlit as st
import pandas as pd

st.title("KvK Helper")

tab_heroes, tab_charms, tab_gov_gear = st.tabs(["Hero Calculator", "Charm Calculator", "Gov Gear Calculator"])

with tab_heroes:
    st.set_page_config(layout="wide")
    st.title("Hero Level Calculator")
    st.write("Use the expanders to open each category. Results appear under each character.")

    # --------------------------
    # Hero Categories
    # --------------------------
    categories = {
        "Mythic": ["Jabel", "Zoe", "Marlin", "Amadeus", "Hilde", "Helga", "Saul"],
        "Epic":   ["Diana", "Quinn", "Howard", "Chenko", "Gordon", "Amane", "Yeonwoo", "Fahd"],
        "Rare":   ["Forrest", "Olive", "Seth", "Edwin"]
    }

    # --------------------------
    # Per-step shard costs
    # --------------------------
    step_costs = {
        "Not recruited":0,"0-0": 10, "0-1": 1, "0-2": 1, "0-3": 2, "0-4": 2, "0-5": 2,
        "1-0": 2, "1-1": 5, "1-2": 5, "1-3": 5, "1-4": 5, "1-5": 15,
        "2-0": 15, "2-1": 15, "2-2": 15, "2-3": 15, "2-4": 15, "2-5": 40,
        "3-0": 40, "3-1": 40, "3-2": 40, "3-3": 40, "3-4": 40, "3-5": 100,
        "4-0": 100, "4-1": 100, "4-2": 100, "4-3": 100, "4-4": 100, "4-5": 100,
        "5-0": 100
    }

    # Ordered list of levels
    levels_ordered = [
        "Not recruited","0-0","0-1","0-2","0-3","0-4","0-5",
        "1-0","1-1","1-2","1-3","1-4","1-5",
        "2-0","2-1","2-2","2-3","2-4","2-5",
        "3-0","3-1","3-2","3-3","3-4","3-5",
        "4-0","4-1","4-2","4-3","4-4","4-5","5-0"
    ]

    # Cumulative total shards for each level
    cumulative_cost = {}
    running = 0
    for lvl in levels_ordered:
        running += step_costs.get(lvl, 0)
        cumulative_cost[lvl] = running

    # Helper: get highest level reachable from total shards
    def get_level_from_total_shards(total_shards):
        for lvl in reversed(levels_ordered):
            if cumulative_cost[lvl] <= total_shards:
                return lvl
        return "Not recruited"

    # --------------------------
    # CSS for visual styling
    # --------------------------
    st.markdown(
        """
        <style>
        .category-box { padding:10px; border-radius:8px; margin-bottom:8px; }
        .result-box { background-color:#ffffff88; padding:6px; border-radius:6px; margin-top:6px; }
        .warn { background-color:#ffdddd; padding:8px; border-radius:6px; margin-top:8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    category_color_map = {
        "Mythic": "#F6C37B",
        "Epic":   "#C9A2F7",
        "Rare":   "#9FD3FF",
    }

    # --------------------------
    # Main UI
    # --------------------------
    for category, heroes in categories.items():

        with st.expander(f"{category} ({len(heroes)} heroes)", expanded=False):

            st.markdown(
                f"<div class='category-box' style='background:{category_color_map.get(category,'#eee')};'>",
                unsafe_allow_html=True,
            )

            # Mode toggle
            mode_by_shards = st.checkbox(
                f"Instead input number of shards",
                key=f"{category}_mode",
            )

            if mode_by_shards:
                # Show shared pool input for this category
                shared_pool = st.number_input(
                    f"General {category} shards available",
                    min_value=0,
                    step=1,
                    value=0,
                    key=f"{category}_shared",
                )
            else:
                # If not in shard mode, set shared_pool to 0 so it won't affect calculations
                shared_pool = 0

            cols = st.columns(3)
            shared_requested_count = 0

            for idx, hero in enumerate(heroes):
                col = cols[idx % 3]
                with col:
                    st.subheader(hero)

                    # Current level
                    cur_key = f"{hero}_current"
                    current = st.select_slider(
                        f"Current level",
                        options=levels_ordered,
                        key=cur_key,
                    )
                    current_cum = cumulative_cost[current]

                    # Only show "Use shared pool" if shard input mode is active
                    if mode_by_shards and hero not in ('Helga', 'Amadeus'):
                        use_shared = st.checkbox(
                            "Use general shards",
                            value=False,
                            key=f"{hero}_use_shared",
                        )
                        if use_shared:
                            shared_requested_count += 1
                    else:
                        # In target mode, shared pool is not used
                        use_shared = False

                    # --- SHARD INPUT MODE ---
                    if mode_by_shards:
                        hero_shards = st.number_input(
                            f"General shards to add",
                            min_value=0,
                            step=1,
                            value=0,
                            key=f"{hero}_personal_shards",
                        )

                        # Total shards including shared pool if allowed
                        total_shards = current_cum + hero_shards + (shared_pool if use_shared else 0)
                        resulting_level = get_level_from_total_shards(total_shards)

                        st.markdown(
                            f"<div class='result-box'>→ resulting level <b>{resulting_level}</b></div>",
                            unsafe_allow_html=True,
                        )

                    # --- TARGET SLIDER MODE ---
                    else:
                        cur_index = levels_ordered.index(current)
                        allowed_targets = levels_ordered[cur_index:]

                        if not allowed_targets:
                            st.info("Already at max level — no higher target possible.")
                            st.markdown(
                                f"<div class='result-box'>At max level — 0 shards needed</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            target = st.select_slider(
                                f"Target level",
                                options=allowed_targets,
                                key=f"{hero}_target",
                            )
                            target_cum = cumulative_cost[target]
                            shards_needed = target_cum - current_cum

                            st.markdown(
                                f"<div class='result-box'>→ <b>{shards_needed}</b> shards needed to reach {target}</div>",
                                unsafe_allow_html=True,
                            )

            # Warning if shared pool over-allocated
            if shared_requested_count > shared_pool:
                deficit = shared_requested_count - shared_pool
                st.markdown(
                    f"<div class='warn'>⚠ Shared pool over-allocated!<br>"
                    f"Requested by {shared_requested_count} heroes, available: {shared_pool}<br>"
                    f"Short by: {deficit}</div>",
                    unsafe_allow_html=True,
                )
            elif shared_requested_count > 0:
                st.success(f"Shared pool sufficient: requested {shared_requested_count}, available {shared_pool}.")

            st.markdown("</div>", unsafe_allow_html=True)

            # --------------------------
            # Define points per shard by category
            # --------------------------
    points_per_shard = { "Rare": 350,"Epic": 1220,"Mythic": 3040}

    # Prepare summary data
    summary_data = []

    for category, heroes in categories.items():
        for hero in heroes:
            # Get current and target levels from session state
            cur_level = st.session_state.get(f"{hero}_current", "0-0")
            cur_cum = cumulative_cost[cur_level]

            if st.session_state.get(f"{category}_mode", False):
                # Shard input mode
                hero_shards = st.session_state.get(f"{hero}_personal_shards", 0)
                use_shared = st.session_state.get(f"{hero}_use_shared", False)
                shared_pool = st.session_state.get(f"{category}_shared", 0)

                # Total shards including shared if ticked
                total_shards = cur_cum + hero_shards + (shared_pool if use_shared else 0)
                resulting_level = get_level_from_total_shards(total_shards)

                # Shards needed = total added shards
                shards_needed = total_shards - cur_cum
                target_level = resulting_level

            else:
                # Target slider mode
                target_level = st.session_state.get(f"{hero}_target", cur_level)
                target_cum = cumulative_cost.get(target_level, cur_cum)
                shards_needed = target_cum - cur_cum

            # Points
            points = shards_needed * points_per_shard.get(category, 0)

            # Append row
            summary_data.append({
                "Hero": hero,
                "Category": category,
                "Current Level": cur_level,
                "Target Level": target_level,
                "Shards Needed": shards_needed,
                "KvK Prep Points": points
            })

    # Create DataFrame
    df_summary = pd.DataFrame(summary_data)

    # Calculate total points
    total_points = df_summary["KvK Prep Points"].sum()

    # Display table
    st.markdown("## Total Points")
    st.dataframe(df_summary[["Hero", "Current Level", "Target Level", "Shards Needed", "KvK Prep Points"]])

    st.markdown(f"**Total Points:** {total_points:,}")

with tab_charms:

    st.title("Charm Calculator")

    # --------------------------
    # Charm categories
    # --------------------------
    charm_categories = {
        "Infantry": ["Charm I", "Charm II", "Charm III", "Charm IV", "Charm V", "Charm VI"],
        "Archer": ["Charm I", "Charm II", "Charm III", "Charm IV", "Charm V", "Charm VI"],
        "Cavalry": ["Charm I", "Charm II", "Charm III", "Charm IV", "Charm V", "Charm VI"],
    }

    # Charm levels
    levels = [str(i) for i in range(12)]

    # --------------------------
    # Items needed per level up
    # --------------------------
    level_requirements = {
        "0→1": {"designs": 5, "guides": 5},
        "1→2": {"designs": 15, "guides": 40},
        "2→3": {"designs": 40, "guides": 60},
        "3→4": {"designs": 100, "guides": 80},
        "4→5": {"designs": 200, "guides": 100},
        "5→6": {"designs": 300, "guides": 120},
        "6→7": {"designs": 400, "guides": 140},
        "7→8": {"designs": 400, "guides": 200},
        "8→9": {"designs": 400, "guides": 300},
        "9→10": {"designs": 420, "guides": 420},
        "10→11": {"designs": 420, "guides": 560}
    }

    # --------------------------
    # Points per level up
    # --------------------------
    points_per_level = {
        1: 625, 2: 1250, 3: 3125, 4: 8750, 5: 11250,
        6: 12500, 7: 12500, 8: 13000, 9: 14000,
        10: 15000, 11: 16000
    }

    # --------------------------
    # Helper functions
    # --------------------------
    def items_needed(current, target):
        current_idx = int(current)
        target_idx = int(target)
        total = {"designs": 0, "guides": 0, "points": 0}
        for lvl in range(current_idx, target_idx):
            key = f"{lvl}→{lvl + 1}"
            req = level_requirements[key]
            total["designs"] += req["designs"]
            total["guides"] += req["guides"]
            total["points"] += points_per_level[lvl + 1]
        return total

    def max_levels_global(current_levels_all, total_designs, total_guides, charm_categories_priority):
        """Greedy allocation across all charms with category priority"""
        final_levels = current_levels_all.copy()
        resources_left = {"designs": total_designs, "guides": total_guides}
        total_points = 0

        def category_priority_index(category):
            return charm_categories_priority.index(category)

        upgrade_possible = True
        while upgrade_possible:
            upgrade_possible = False
            best_charm = None
            best_value = 0
            for category in charm_categories_priority:
                for charm in charm_categories[category]:
                    key_name = f"{category}_{charm}"
                    cur_level = int(final_levels[key_name])
                    if cur_level >= 11:
                        continue
                    next_level = str(cur_level + 1)
                    req = level_requirements[f"{cur_level}→{cur_level + 1}"]
                    if resources_left["designs"] >= req["designs"] and resources_left["guides"] >= req["guides"]:
                        total_req = req["designs"] + req["guides"]
                        value = points_per_level[cur_level + 1] / total_req
                        # Break ties using category priority
                        if value > best_value or (value == best_value and best_charm and category_priority_index(category) < category_priority_index(best_charm.split("_")[0])):
                            best_value = value
                            best_charm = key_name
                            best_req = req
                            best_next_level = next_level
            if best_charm:
                final_levels[best_charm] = best_next_level
                resources_left["designs"] -= best_req["designs"]
                resources_left["guides"] -= best_req["guides"]
                total_points += points_per_level[int(best_next_level)]
                upgrade_possible = True

        return final_levels, resources_left, total_points

    # --------------------------
    # UI
    # --------------------------
    # Checkbox for global resource-input mode
    mode_by_items = st.checkbox("Resource Input Mode (maximize points with total resources)", key="charms_resource_mode")

    # Collect current and target levels
    results = []
    current_levels_all = {}

    for category, charms in charm_categories.items():
        with st.expander(f"{category} Charms", expanded=False):
            cols = st.columns(3)
            for idx, charm in enumerate(charms):
                col = cols[idx % 3]
                with col:
                    st.subheader(charm)
                    key_name = f"{category}_{charm}"
                    # Current level
                    current_levels_all[key_name] = st.select_slider(
                        "Current Level",
                        options=levels,
                        key=f"{category}_{charm}_current"
                    )

                    if not mode_by_items:
                        # Target level slider directly below current level
                        cur_idx = int(current_levels_all[key_name])
                        allowed_targets = levels[cur_idx:]
                        target_level = st.select_slider(
                            "Target Level",
                            options=allowed_targets,
                            key=f"{category}_{charm}_target"
                        )
                        needed = items_needed(current_levels_all[key_name], target_level)
                        st.markdown(
                            f"<div style='background:#333;color:white;padding:6px;border-radius:5px;'>"
                            f"→ Designs: <b>{needed['designs']}</b>, Guides: <b>{needed['guides']}</b>, Points: <b>{needed['points']}</b>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        results.append({
                            "Category": category,
                            "Charm": charm,
                            "Current Level": current_levels_all[key_name],
                            "Target Level": target_level,
                            "Designs Needed": needed["designs"],
                            "Guides Needed": needed["guides"],
                            "Points": needed["points"]
                        })

    # --------------------------
    # Resource input mode
    # --------------------------
    if mode_by_items:
        st.header("Total Available Resources")
        total_designs = st.number_input("Total Designs", min_value=0, step=1, key="charms_total_designs")
        total_guides = st.number_input("Total Guides", min_value=0, step=1, key="charms_total_guides")

        if st.button("Calculate Optimal Upgrades", key="charms_calc_button"):
            priority_list = ["Infantry", "Archer", "Cavalry"]
            final_levels, remaining, total_points = max_levels_global(
                current_levels_all, total_designs, total_guides, priority_list
            )

            st.subheader("Final Levels per Charm")
            for key, level in final_levels.items():
                category, charm = key.split("_")
                st.write(f"{category} {charm}: {level}")

            st.subheader("Resources Left Over")
            st.write(f"Designs: {remaining['designs']}, Guides: {remaining['guides']}")
            st.subheader("Total Points Gained")
            st.write(f"{total_points:,}")

            # Build summary table
            for key, level in final_levels.items():
                category, charm = key.split("_")
                cur_level = int(current_levels_all[key])
                target_level = int(level)
                needed = items_needed(cur_level, target_level)
                results.append({
                    "Category": category,
                    "Charm": charm,
                    "Current Level": cur_level,
                    "Target Level": target_level,
                    "Designs Needed": needed["designs"],
                    "Guides Needed": needed["guides"],
                    "Points": needed["points"]
                })

    # --------------------------
    # Summary table
    # --------------------------
    if results:
        st.markdown("## Summary Table")
        df_summary = pd.DataFrame(results)
        st.dataframe(df_summary[
            ["Category", "Charm", "Current Level", "Target Level", "Designs Needed", "Guides Needed", "Points"]
        ])
        st.markdown(f"**Total Points:** {df_summary['Points'].sum():,}")

with tab_gov_gear:
    st.title("Gov Gear Calculator")

    # --------------------------
    # Gov Gear Items
    # --------------------------
    gov_gear_items = ["Cap", "Watch", "Coat", "Trousers", "Belt", "Weapon"]

    # Levels / rarities
    rarities = [
        "None","Uncommon", "Uncommon (1-Star)", "Rare", "Rare (1-Star)", "Rare (2-Star)", "Rare (3-Star)",
        "Epic", "Epic (1-Star)", "Epic (2-Star)", "Epic (3-Star)",
        "Epic T1", "Epic T1 (1-Star)", "Epic T1 (2-Star)", "Epic T1 (3-Star)",
        "Mythic", "Mythic (1-Star)", "Mythic (2-Star)", "Mythic (3-Star)"
    ]

    # --------------------------
    # Materials needed per level up
    # --------------------------
    # Example structure: 'current→next': {"threads": X, "satins": Y, "papers": Z}
    # Fill in the real numbers for each level
    gov_gear_requirements = gov_gear_requirements = {
        "None→Uncommon": {"threads": 15, "satins": 1500, "papers": 0},
        # Uncommon
        "Uncommon→Uncommon (1-Star)": {"threads": 40, "satins": 3800, "papers": 0},

        # Rare
        "Uncommon (1-Star)→Rare": {"threads": 70, "satins": 7000, "papers": 0},
        "Rare→Rare (1-Star)": {"threads": 95, "satins": 9700, "papers": 0},
        "Rare (1-Star)→Rare (2-Star)": {"threads": 10, "satins": 1000, "papers": 45},
        "Rare (2-Star)→Rare (3-Star)": {"threads": 10, "satins": 1000, "papers": 50},

        # Epic
        "Rare (3-Star)→Epic": {"threads": 15, "satins": 1500, "papers": 60},
        "Epic→Epic (1-Star)": {"threads": 15, "satins": 1500, "papers": 70},
        "Epic (1-Star)→Epic (2-Star)": {"threads": 65, "satins": 6500, "papers": 40},
        "Epic (2-Star)→Epic (3-Star)": {"threads": 80, "satins": 8000, "papers": 50},

        # Epic T1
        "Epic (3-Star)→Epic T1": {"threads": 95, "satins": 10000, "papers": 60},
        "Epic T1→Epic T1 (1-Star)": {"threads": 110, "satins": 11000, "papers": 70},
        "Epic T1 (1-Star)→Epic T1 (2-Star)": {"threads": 130, "satins": 13000, "papers": 85},
        "Epic T1 (2-Star)→Epic T1 (3-Star)": {"threads": 160, "satins": 15000, "papers": 100},

        # Mythic
        "Epic T1 (3-Star)→Mythic": {"threads": 220, "satins": 22000, "papers": 40},
        "Mythic→Mythic (1-Star)": {"threads": 230, "satins": 23000, "papers": 45},
        "Mythic (1-Star)→Mythic (2-Star)": {"threads": 250, "satins": 25000, "papers": 45},
        "Mythic (2-Star)→Mythic (3-Star)": {"threads": 260, "satins": 26000, "papers": 45},
    }


    # --------------------------
    # Points per level
    # --------------------------
    points_per_rarity = {
        "Uncommon": 1125,
        "Uncommon (1-Star)": 1875,
        "Rare": 3000,
        "Rare (1-Star)": 4500,
        "Rare (2-Star)": 5100,
        "Rare (3-Star)": 5400,
        "Epic": 3230,
        "Epic (1-Star)": 3230,
        "Epic (2-Star)": 3225,
        "Epic (3-Star)": 3225,
        "Epic T1": 3440,
        "Epic T1 (1-Star)": 3440,
        "Epic T1 (2-Star)": 4085,
        "Epic T1 (3-Star)": 4085,
        "Mythic": 6250,
        "Mythic (1-Star)": 6250,
        "Mythic (2-Star)": 6250,
        "Mythic (3-Star)": 6250
    }


    # --------------------------
    # Helper functions
    # --------------------------
    def materials_needed(current, target):
        cur_idx = rarities.index(current)
        target_idx = rarities.index(target)
        total = {"threads": 0, "satins": 0, "papers": 0, "points": 0}
        for idx in range(cur_idx, target_idx):
            key = f"{rarities[idx]}→{rarities[idx + 1]}"
            req = gov_gear_requirements.get(key, {"threads": 0, "satins": 0, "papers": 0})
            total["threads"] += req["threads"]
            total["satins"] += req["satins"]
            total["papers"] += req["papers"]
            total["points"] += points_per_rarity[rarities[idx + 1]]
        return total


    def max_rarity_from_resources(current, threads, satins, papers):
        final_levels = {}
        resources_left = {"threads": threads, "satins": satins, "papers": papers}
        total_points = 0

        # Start with current levels
        for item, cur in current.items():
            final_levels[item] = cur

        # Greedy allocation: upgrade item that gives most points per resource
        upgrade_possible = True
        while upgrade_possible:
            upgrade_possible = False
            best_item = None
            best_value = 0
            for item, cur in final_levels.items():
                cur_idx = rarities.index(cur)
                if cur_idx >= len(rarities) - 1:
                    continue
                next_level = rarities[cur_idx + 1]
                key = f"{cur}→{next_level}"
                req = gov_gear_requirements.get(key, {"threads": 0, "satins": 0, "papers": 0})
                if (resources_left["threads"] >= req["threads"] and
                        resources_left["satins"] >= req["satins"] and
                        resources_left["papers"] >= req["papers"]):
                    total_req = req["threads"] + req["satins"] + req["papers"]
                    value = points_per_rarity[next_level] / (total_req if total_req > 0 else 1)
                    if value > best_value:
                        best_value = value
                        best_item = item
                        best_req = req
                        best_next_level = next_level
            if best_item:
                final_levels[best_item] = best_next_level
                resources_left["threads"] -= best_req["threads"]
                resources_left["satins"] -= best_req["satins"]
                resources_left["papers"] -= best_req["papers"]
                total_points += points_per_rarity[best_next_level]
                upgrade_possible = True

        return final_levels, resources_left, total_points


    # --------------------------
    # UI
    # --------------------------



    # --------------------------
    # Mode selection
    # --------------------------
    mode_by_resources = st.checkbox("Resource Input Mode (maximize points with total resources)")

    current_levels = {}
    results = []

    # --------------------------
    # Current + Target sliders for each item
    # --------------------------
    cols = st.columns(3)
    for idx, item in enumerate(gov_gear_items):
        col = cols[idx % 3]
        with col:
            # Current level slider
            current_levels[item] = st.select_slider(
                f"{item} Current Level",
                options=rarities,
                key=f"{item}_current"
            )

            if not mode_by_resources:
                # Target-level mode
                cur_idx = rarities.index(current_levels[item])
                allowed_targets = rarities[cur_idx:]
                if allowed_targets:
                    target = st.select_slider(
                        f"{item} Target Level",
                        options=allowed_targets,
                        key=f"{item}_target"
                    )
                    needed = materials_needed(current_levels[item], target)
                    st.markdown(
                        f"<div style='background:#333;color:white;padding:6px;border-radius:5px;'>"
                        f"→ Threads: <b>{needed['threads']}</b>, "
                        f"Satins: <b>{needed['satins']}</b>, "
                        f"Artisans: <b>{needed['papers']}</b>, "
                        f"Points: <b>{needed['points']}</b>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    results.append({
                        "Item": item,
                        "Current": current_levels[item],
                        "Target": target,
                        "Threads Needed": needed["threads"],
                        "Satins Needed": needed["satins"],
                        "Papers Needed": needed["papers"],
                        "Points": needed["points"]
                    })
                else:
                    st.info("Already at max rarity.")
                    results.append({
                        "Item": item,
                        "Current": current_levels[item],
                        "Target": current_levels[item],
                        "Threads Needed": 0,
                        "Satins Needed": 0,
                        "Papers Needed": 0,
                        "Points": 0
                    })

    # --------------------------
    # Resource-input mode
    # --------------------------
    if mode_by_resources:
        st.header("Total Available Resources")
        total_threads = st.number_input("Threads", min_value=0, step=1)
        total_satins = st.number_input("Satins", min_value=0, step=1)
        total_papers = st.number_input("Papers", min_value=0, step=1)

        if st.button("Calculate Optimal Upgrades"):
            final_levels, remaining, total_points = max_rarity_from_resources(
                current_levels, total_threads, total_satins, total_papers
            )
            st.subheader("Final Levels per Item")
            for item, level in final_levels.items():
                st.write(f"{item}: {level}")
            st.subheader("Resources Left Over")
            st.write(
                f"Threads: {remaining['threads']}, Satins: {remaining['satins']}, Papers: {remaining['papers']}"
            )
            st.subheader("Total Points Gained")
            st.write(f"{total_points:,}")

    # --------------------------
    # Summary Table for Target Mode
    # --------------------------
    if results:
        st.markdown("## Summary Table")
        import pandas as pd
        df_summary = pd.DataFrame(results)
        st.dataframe(
            df_summary[["Item", "Current", "Target", "Threads Needed", "Satins Needed", "Papers Needed", "Points"]]
        )
        st.markdown(f"**Total Points:** {df_summary['Points'].sum():,}")













