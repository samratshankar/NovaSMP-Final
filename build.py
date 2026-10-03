import os
import struct
import zlib
import zipfile

def create_png(width, height, color):
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    raw_data = b''.join(b'\x00' + bytes(color) * width for _ in range(height))
    idat = chunk(b'IDAT', zlib.compress(raw_data))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

def write_file(path, content, is_binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = 'wb' if is_binary else 'w'
    with open(path, mode, encoding=None if is_binary else 'utf-8') as f:
        f.write(content)

print("[1/4] Building Resource Pack directory...")

write_file("NovaSMP-ResourcePack/pack.mcmeta", '''{
  "pack": {
    "pack_format": 46,
    "description": "§6NovaSMP Official Assets §7- Stellar Cores & HUD"
  }
}''')

write_file("NovaSMP-ResourcePack/assets/minecraft/font/default.json", '''{
  "providers": [
    {
      "type": "bitmap",
      "file": "minecraft:font/star_filled.png",
      "ascent": 7,
      "height": 8,
      "chars": ["\\uE001"]
    },
    {
      "type": "bitmap",
      "file": "minecraft:font/star_empty.png",
      "ascent": 7,
      "height": 8,
      "chars": ["\\uE002"]
    }
  ]
}''')

write_file("NovaSMP-ResourcePack/assets/minecraft/models/item/fire_charge.json", '''{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "minecraft:item/fire_charge"
  },
  "overrides": [
    {
      "predicate": { "custom_model_data": 7701 },
      "model": "nova:item/nova_essence"
    }
  ]
}''')

write_file("NovaSMP-ResourcePack/assets/minecraft/models/nova/item/nova_essence.json", '''{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "nova:item/nova_essence"
  },
  "display": {
    "thirdperson_righthand": { "rotation": [0, 90, -35], "translation": [0, 1.25, -3.5], "scale": [0.85, 0.85, 0.85] },
    "firstperson_righthand": { "rotation": [0, -45, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.72, 0.72, 0.72] },
    "ground": { "rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.85, 0.85, 0.85] },
    "gui": { "rotation": [30, 225, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0] }
  }
}''')

write_file("NovaSMP-ResourcePack/assets/minecraft/textures/nova/item/nova_essence.png.mcmeta", '''{
  "animation": { "frametime": 3, "interpolate": true }
}''')

write_file("NovaSMP-ResourcePack/pack.png", create_png(64, 64, (255, 140, 0, 255)), is_binary=True)
write_file("NovaSMP-ResourcePack/assets/minecraft/textures/font/star_filled.png", create_png(8, 8, (255, 170, 0, 255)), is_binary=True)
write_file("NovaSMP-ResourcePack/assets/minecraft/textures/font/star_empty.png", create_png(8, 8, (60, 60, 60, 255)), is_binary=True)
write_file("NovaSMP-ResourcePack/assets/minecraft/textures/nova/item/nova_essence.png", create_png(16, 16, (255, 120, 20, 255)), is_binary=True)

print("[2/4] Zipping NovaSMP-ResourcePack.zip...")
with zipfile.ZipFile("NovaSMP-ResourcePack.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk("NovaSMP-ResourcePack"):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, "NovaSMP-ResourcePack")
            zipf.write(full_path, rel_path)

print("[3/4] Writing Maven Java project...")

write_file("NovaSMP-Plugin/pom.xml", '''<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.novasmp</groupId>
  <artifactId>NovaSMP</artifactId>
  <version>1.0.0</version>
  <properties>
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler.target>21</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <repositories>
    <repository>
      <id>papermc</id>
      <url>https://repo.papermc.io/repository/maven-public/</url>
    </repository>
  </repositories>
  <dependencies>
    <dependency>
      <groupId>io.papermc.paper</groupId>
      <artifactId>paper-api</artifactId>
      <version>1.21.4-R0.1-SNAPSHOT</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.13.0</version>
        <configuration>
          <release>21</release>
        </configuration>
      </plugin>
    </plugins>
    <resources>
      <resource>
        <directory>src/main/resources</directory>
        <filtering>true</filtering>
      </resource>
    </resources>
  </build>
</project>''')

write_file("NovaSMP-Plugin/src/main/resources/plugin.yml", '''name: NovaSMP
version: 1.0.0
main: com.novasmp.NovaSMP
api-version: '1.21'
authors: [NovaSMP]
description: NovaSMP Custom 5-Essence Power Progression Plugin.
commands:
  novabinds:
    description: Open the keybind configuration menu.
    aliases: [binds]
  essenserecipe:
    description: Modify the dynamic Nova Essence crafting recipe.
    permission: nova.admin
  ignite:
    description: Toggle internal stellar body lighting.
  novatoggle:
    description: Toggle power activation safety.
    aliases: [novasafety]
''')

write_file("NovaSMP-Plugin/src/main/resources/config.yml", '''domain:
  world: "world"
  spawn:
    x: 10000.5
    y: 150.0
    z: 10000.5
    yaw: 0.0
    pitch: 0.0
  radius: 20
  duration_seconds: 90

essence-recipe:
  grid:
    - "NETHERITE_INGOT"
    - "NETHER_STAR"
    - "NETHERITE_INGOT"
    - "END_CRYSTAL"
    - "HEART_OF_THE_SEA"
    - "END_CRYSTAL"
    - "BLAZE_ROD"
    - "DRAGON_BREATH"
    - "BLAZE_ROD"
''')

src = "NovaSMP-Plugin/src/main/java/com/novasmp/"

write_file(src + "NovaSMP.java", '''package com.novasmp;

import com.novasmp.commands.*;
import com.novasmp.domain.DomainManager;
import com.novasmp.listeners.*;
import com.novasmp.managers.BindManager;
import com.novasmp.managers.CooldownManager;
import com.novasmp.tasks.DynamicLightTask;
import com.novasmp.tasks.HudTask;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.List;

public final class NovaSMP extends JavaPlugin {
    private static NovaSMP instance;
    private NamespacedKey essenceKey;
    private NamespacedKey safetyKey;
    private NamespacedKey igniteKey;
    private BindManager bindManager;
    private CooldownManager cooldownManager;
    private DomainManager domainManager;

    @Override
    public void onEnable() {
        instance = this;
        saveDefaultConfig();

        essenceKey = new NamespacedKey(this, "nova_essence");
        safetyKey = new NamespacedKey(this, "nova_safety");
        igniteKey = new NamespacedKey(this, "nova_ignite");

        cooldownManager = new CooldownManager();
        bindManager = new BindManager(this);
        domainManager = new DomainManager(this);

        getServer().getPluginManager().registerEvents(new EssenceListener(this), this);
        getServer().getPluginManager().registerEvents(new PowerExecutionListener(this), this);
        getServer().getPluginManager().registerEvents(bindManager, this);
        getServer().getPluginManager().registerEvents(new RecipeEditorListener(this), this);
        getServer().getPluginManager().registerEvents(domainManager, this);

        getCommand("novabinds").setExecutor(new BindsCommand(this));
        getCommand("essenserecipe").setExecutor(new RecipeCommand(this));
        getCommand("ignite").setExecutor(new IgniteCommand(this));
        getCommand("novatoggle").setExecutor(new ToggleSafetyCommand(this));

        new HudTask(this).runTaskTimer(this, 0L, 5L);
        new DynamicLightTask(this).runTaskTimer(this, 0L, 4L);

        new RecipeEditorListener(this).registerCurrentRecipe();
    }

    @Override
    public void onDisable() {
        if (domainManager != null) domainManager.emergencyCleanup();
    }

    public static NovaSMP getInstance() { return instance; }
    public NamespacedKey getEssenceKey() { return essenceKey; }
    public NamespacedKey getSafetyKey() { return safetyKey; }
    public NamespacedKey getIgniteKey() { return igniteKey; }
    public BindManager getBindManager() { return bindManager; }
    public CooldownManager getCooldownManager() { return cooldownManager; }
    public DomainManager getDomainManager() { return domainManager; }

    public int getEssence(Player p) {
        return p.getPersistentDataContainer().getOrDefault(essenceKey, PersistentDataType.INTEGER, 0);
    }

    public void setEssence(Player p, int amt) {
        p.getPersistentDataContainer().set(essenceKey, PersistentDataType.INTEGER, Math.max(0, Math.min(5, amt)));
    }

    public boolean isSafetyToggled(Player p) {
        return p.getPersistentDataContainer().getOrDefault(safetyKey, PersistentDataType.BYTE, (byte) 0) == 1;
    }

    public void setSafetyToggled(Player p, boolean t) {
        p.getPersistentDataContainer().set(safetyKey, PersistentDataType.BYTE, t ? (byte) 1 : (byte) 0);
    }

    public boolean isIgnited(Player p) {
        return p.getPersistentDataContainer().getOrDefault(igniteKey, PersistentDataType.BYTE, (byte) 0) == 1;
    }

    public void setIgnited(Player p, boolean i) {
        p.getPersistentDataContainer().set(igniteKey, PersistentDataType.BYTE, i ? (byte) 1 : (byte) 0);
    }

    public ItemStack createNovaEssence(int amount) {
        ItemStack item = new ItemStack(Material.FIRE_CHARGE, amount);
        ItemMeta meta = item.getItemMeta();
        meta.setDisplayName("§6§l✦ NOVA ESSENCE ✦");
        meta.setCustomModelData(7701);
        meta.setLore(List.of(
            "§8Bound Stellar Fragment",
            "",
            "§eRight-Click: §fAbsorb core (§6+1 Tier§f)",
            "§cShift + Right-Click: §fCondense into physical form",
            "",
            "§6§o\\"A drop of thermonuclear fire, torn from a dying star.\\""
        ));
        item.setItemMeta(meta);
        return item;
    }
}''')

write_file(src + "managers/CooldownManager.java", '''package com.novasmp.managers;

import org.bukkit.entity.Player;
import java.util.HashMap;
import java.util.Map;

public class CooldownManager {
    private final Map<String, Long> cooldowns = new HashMap<>();

    public boolean isOnCooldown(Player player, String ability) {
        String key = player.getUniqueId() + ":" + ability;
        return cooldowns.containsKey(key) && cooldowns.get(key) > System.currentTimeMillis();
    }

    public long getRemainingSeconds(Player player, String ability) {
        String key = player.getUniqueId() + ":" + ability;
        if (!cooldowns.containsKey(key)) return 0;
        return Math.max(0, (cooldowns.get(key) - System.currentTimeMillis()) / 1000);
    }

    public void setCooldown(Player player, String ability, int seconds) {
        String key = player.getUniqueId() + ":" + ability;
        cooldowns.put(key, System.currentTimeMillis() + (seconds * 1000L));
    }
}''')

write_file(src + "managers/BindManager.java", '''package com.novasmp.managers;

import com.novasmp.NovaSMP;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;

import java.util.*;

public class BindManager implements Listener {
    public enum TriggerType {
        SNEAK_F("Sneak + Swap (F)"),
        SNEAK_JUMP("Sneak + Jump"),
        DOUBLE_SNEAK("Double-Tap Sneak"),
        SNEAK_RIGHT_CLICK("Sneak + Right-Click"),
        SNEAK_DROP("Sneak + Drop (Q)"),
        SNEAK_LEFT_CLICK("Sneak + Punch");

        public final String display;
        TriggerType(String display) { this.display = display; }
    }

    private final NovaSMP plugin;
    public static final String GUI_TITLE = "§8Customize Nova Keybinds";
    public static final Map<String, TriggerType> DEFAULTS = new LinkedHashMap<>();
    static {
        DEFAULTS.put("merchants_favor", TriggerType.SNEAK_F);
        DEFAULTS.put("thermo_smelt", TriggerType.SNEAK_LEFT_CLICK);
        DEFAULTS.put("stellar_leap", TriggerType.SNEAK_JUMP);
        DEFAULTS.put("constellation_step", TriggerType.DOUBLE_SNEAK);
        DEFAULTS.put("supernova_repulsion", TriggerType.SNEAK_F);
        DEFAULTS.put("supernova_pulse", TriggerType.SNEAK_RIGHT_CLICK);
        DEFAULTS.put("supernova_domain", TriggerType.SNEAK_DROP);
    }

    public BindManager(NovaSMP plugin) { this.plugin = plugin; }

    public void openGUI(Player player) {
        Inventory gui = Bukkit.createInventory(null, 27, GUI_TITLE);
        int[] slots = {10, 11, 12, 13, 14, 15, 16};
        int idx = 0;
        for (Map.Entry<String, TriggerType> entry : DEFAULTS.entrySet()) {
            String powerId = entry.getKey();
            TriggerType active = getPlayerBind(player, powerId);
            ItemStack icon = new ItemStack(Material.FIREWORK_STAR);
            ItemMeta meta = icon.getItemMeta();
            meta.setDisplayName("§6§l" + formatName(powerId));
            meta.setLore(List.of("§7Keybind: §e" + active.display, "", "§aLeft-Click: §fCycle to next keybind", "§cRight-Click: §fReset to default"));
            icon.setItemMeta(meta);
            gui.setItem(slots[idx++], icon);
        }
        player.openInventory(gui);
    }

    @EventHandler
    public void onGuiClick(InventoryClickEvent event) {
        if (!event.getView().getTitle().equals(GUI_TITLE)) return;
        event.setCancelled(true);
        if (!(event.getWhoClicked() instanceof Player player)) return;
        ItemStack clicked = event.getCurrentItem();
        if (clicked == null || !clicked.hasItemMeta()) return;

        String powerId = clicked.getItemMeta().getDisplayName().replace("§6§l", "").toLowerCase().replace(" ", "_");
        if (!DEFAULTS.containsKey(powerId)) return;

        TriggerType current = getPlayerBind(player, powerId);
        if (event.isRightClick()) {
            setPlayerBind(player, powerId, DEFAULTS.get(powerId));
        } else {
            TriggerType[] vals = TriggerType.values();
            setPlayerBind(player, powerId, vals[(current.ordinal() + 1) % vals.length]);
        }
        player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 1.0f, 1.0f);
        openGUI(player);
    }

    public TriggerType getPlayerBind(Player player, String powerId) {
        PersistentDataContainer pdc = player.getPersistentDataContainer();
        String val = pdc.get(new NamespacedKey(plugin, "bind_" + powerId), PersistentDataType.STRING);
        return val != null ? TriggerType.valueOf(val) : DEFAULTS.getOrDefault(powerId, TriggerType.SNEAK_F);
    }

    public void setPlayerBind(Player player, String powerId, TriggerType trigger) {
        player.getPersistentDataContainer().set(new NamespacedKey(plugin, "bind_" + powerId), PersistentDataType.STRING, trigger.name());
    }

    private String formatName(String id) {
        String[] parts = id.split("_");
        StringBuilder sb = new StringBuilder();
        for (String p : parts) sb.append(Character.toUpperCase(p.charAt(0))).append(p.substring(1)).append(" ");
        return sb.toString().trim();
    }
}''')

write_file(src + "domain/DomainManager.java", '''package com.novasmp.domain;

import com.novasmp.NovaSMP;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.scheduler.BukkitRunnable;

import java.util.*;

public class DomainManager implements Listener {
    private final NovaSMP plugin;
    private final Map<UUID, Location> originLocations = new HashMap<>();
    private final Set<Player> activeDomainPlayers = new HashSet<>();
    private final Map<Location, BlockData> alteredBlocks = new HashMap<>();
    private BossBar activeBossBar;
    private BukkitRunnable activeTask;

    public DomainManager(NovaSMP plugin) { this.plugin = plugin; }

    public void startDomain(Player caster, List<Player> participants) {
        activeDomainPlayers.addAll(participants);
        World domainWorld = Bukkit.getWorld(plugin.getConfig().getString("domain.world", "world"));
        Location domainCenter = new Location(domainWorld, plugin.getConfig().getDouble("domain.spawn.x"), plugin.getConfig().getDouble("domain.spawn.y"), plugin.getConfig().getDouble("domain.spawn.z"));

        for (Player p : participants) {
            originLocations.put(p.getUniqueId(), p.getLocation());
            p.teleport(domainCenter);
            p.playSound(domainCenter, Sound.BLOCK_END_PORTAL_SPAWN, 1.0f, 1.2f);
        }

        activeBossBar = Bukkit.createBossBar("§5§l✦ SUPERNOVA DOMAIN §8| §e1:30", BarColor.PURPLE, BarStyle.SEGMENTED_10);
        participants.forEach(activeBossBar::addPlayer);
        int totalSeconds = plugin.getConfig().getInt("domain.duration_seconds", 90);

        activeTask = new BukkitRunnable() {
            int secondsLeft = totalSeconds;
            @Override
            public void run() {
                activeDomainPlayers.removeIf(p -> !p.isOnline() || p.isDead());
                if (activeDomainPlayers.size() <= 1 || secondsLeft <= 0) {
                    endDomain();
                    cancel();
                    return;
                }
                secondsLeft--;
                activeBossBar.setProgress(Math.max(0.0, (double) secondsLeft / totalSeconds));
                if (secondsLeft <= 15) {
                    activeBossBar.setColor(BarColor.RED);
                    activeBossBar.setTitle("§4§l⚠ COLLAPSE IMMINENT §8| §c" + secondsLeft + "s");
                }
            }
        };
        activeTask.runTaskTimer(plugin, 0L, 20L);
    }

    @EventHandler
    public void onBlockPlace(BlockPlaceEvent event) {
        if (activeDomainPlayers.contains(event.getPlayer())) {
            Block block = event.getBlock();
            alteredBlocks.putIfAbsent(block.getLocation(), block.getBlockData());
        }
    }

    @EventHandler
    public void onDomainDeath(PlayerDeathEvent event) {
        Player victim = event.getEntity();
        if (!activeDomainPlayers.contains(victim)) return;
        activeDomainPlayers.remove(victim);
        Location origin = originLocations.remove(victim.getUniqueId());
        if (originLocations.size() == 1 && origin != null) {
            List<org.bukkit.inventory.ItemStack> drops = new ArrayList<>(event.getDrops());
            event.getDrops().clear();
            for (org.bukkit.inventory.ItemStack drop : drops) origin.getWorld().dropItemNaturally(origin, drop);
        }
    }

    public void endDomain() {
        if (activeBossBar != null) activeBossBar.removeAll();
        for (Player p : activeDomainPlayers) {
            Location origin = originLocations.remove(p.getUniqueId());
            if (origin != null && p.isOnline()) p.teleport(origin);
        }
        for (Map.Entry<Location, BlockData> entry : alteredBlocks.entrySet()) {
            entry.getKey().getBlock().setType(Material.AIR);
        }
        alteredBlocks.clear();
        activeDomainPlayers.clear();
    }

    public void emergencyCleanup() {
        if (activeTask != null) activeTask.cancel();
        endDomain();
    }
}''')

write_file(src + "tasks/HudTask.java", '''package com.novasmp.tasks;

import com.novasmp.NovaSMP;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.scheduler.BukkitRunnable;

public class HudTask extends BukkitRunnable {
    private final NovaSMP plugin;
    public HudTask(NovaSMP plugin) { this.plugin = plugin; }

    @Override
    public void run() {
        for (Player player : Bukkit.getOnlinePlayers()) {
            int essence = plugin.getEssence(player);
            StringBuilder stars = new StringBuilder();
            for (int i = 1; i <= 5; i++) {
                stars.append(i <= essence ? "§6\\uE001 " : "§8\\uE002 ");
            }

            String hud;
            if (essence == 0) {
                hud = "§8[ " + stars.toString().trim() + " §8] §cEXTINGUISHED";
            } else {
                long leap = plugin.getCooldownManager().getRemainingSeconds(player, "stellar_leap");
                long rep = plugin.getCooldownManager().getRemainingSeconds(player, "supernova_repulsion");
                long dom = plugin.getCooldownManager().getRemainingSeconds(player, "supernova_domain");
                String status = (essence >= 5) ? "§5DOMAIN: " + (dom > 0 ? "§c" + dom + "s" : "§aREADY")
                              : (essence >= 4) ? "§6REPULSION: " + (rep > 0 ? "§c" + rep + "s" : "§aREADY")
                              : "§eLEAP: " + (leap > 0 ? "§c" + leap + "s" : "§aREADY");
                hud = "§8[ " + stars.toString().trim() + " §8]  " + status;
            }
            player.spigot().sendMessage(ChatMessageType.ACTION_BAR, new TextComponent(hud));
        }
    }
}''')

write_file(src + "tasks/DynamicLightTask.java", '''package com.novasmp.tasks;

import com.novasmp.NovaSMP;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.block.data.type.Light;
import org.bukkit.entity.Player;
import org.bukkit.scheduler.BukkitRunnable;

import java.util.*;

public class DynamicLightTask extends BukkitRunnable {
    private final NovaSMP plugin;
    private final Map<UUID, Block> lastBlocks = new HashMap<>();

    public DynamicLightTask(NovaSMP plugin) { this.plugin = plugin; }

    @Override
    public void run() {
        for (Player p : Bukkit.getOnlinePlayers()) {
            UUID id = p.getUniqueId();
            if (!plugin.isIgnited(p) || plugin.getEssence(p) == 0) {
                clearLight(id);
                continue;
            }
            int lvl = switch (plugin.getEssence(p)) {
                case 1 -> 4; case 2 -> 7; case 3 -> 10; case 4 -> 13; case 5 -> 15; default -> 0;
            };
            Block cur = p.getLocation().getBlock();
            Block old = lastBlocks.get(id);
            if (old != null && !old.equals(cur) && old.getType() == Material.LIGHT) old.setType(Material.AIR);
            if (cur.getType() == Material.AIR) {
                cur.setType(Material.LIGHT);
                Light l = (Light) cur.getBlockData();
                l.setLevel(lvl);
                cur.setBlockData(l);
                lastBlocks.put(id, cur);
            }
        }
    }

    private void clearLight(UUID id) {
        Block old = lastBlocks.remove(id);
        if (old != null && old.getType() == Material.LIGHT) old.setType(Material.AIR);
    }
}''')

write_file(src + "listeners/EssenceListener.java", '''package com.novasmp.listeners;

import com.novasmp.NovaSMP;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.inventory.ItemStack;

public class EssenceListener implements Listener {
    private final NovaSMP plugin;
    public EssenceListener(NovaSMP plugin) { this.plugin = plugin; }

    @EventHandler(priority = EventPriority.HIGH)
    public void onDeath(PlayerDeathEvent e) {
        Player victim = e.getEntity();
        Player killer = victim.getKiller();
        int vicEss = plugin.getEssence(victim);
        if (vicEss > 0) {
            plugin.setEssence(victim, vicEss - 1);
            victim.getWorld().dropItemNaturally(victim.getLocation(), plugin.createNovaEssence(1));
        }
        if (killer != null && !killer.equals(victim)) {
            int kilEss = plugin.getEssence(killer);
            if (kilEss < 5) plugin.setEssence(killer, kilEss + 1);
        }
    }

    @EventHandler
    public void onInteract(PlayerInteractEvent e) {
        Player p = e.getPlayer();
        ItemStack hand = p.getInventory().getItemInMainHand();
        if (hand == null || !hand.hasItemMeta() || !hand.getItemMeta().hasCustomModelData()) return;
        if (hand.getItemMeta().getCustomModelData() != 7701) return;

        if (e.getAction() == Action.RIGHT_CLICK_AIR || e.getAction() == Action.RIGHT_CLICK_BLOCK) {
            e.setCancelled(true);
            int cur = plugin.getEssence(p);
            if (p.isSneaking()) {
                if (cur > 0) {
                    plugin.setEssence(p, cur - 1);
                    p.getInventory().addItem(plugin.createNovaEssence(1));
                }
            } else {
                if (cur < 5) {
                    hand.setAmount(hand.getAmount() - 1);
                    plugin.setEssence(p, cur + 1);
                    p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.5f);
                }
            }
        }
    }
}''')

write_file(src + "listeners/RecipeEditorListener.java", '''package com.novasmp.listeners;

import com.novasmp.NovaSMP;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryCloseEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.ShapedRecipe;

import java.util.*;

public class RecipeEditorListener implements Listener {
    private final NovaSMP plugin;
    public static final String GUI_NAME = "§8[Nova Admin] §6Essence Recipe";
    private final NamespacedKey recipeKey;
    private final int[] slots = {2, 3, 4, 11, 12, 13, 20, 21, 22};

    public RecipeEditorListener(NovaSMP plugin) {
        this.plugin = plugin;
        this.recipeKey = new NamespacedKey(plugin, "dynamic_nova_recipe");
    }

    public void openEditor(Player p) {
        Inventory gui = Bukkit.createInventory(null, 27, GUI_NAME);
        ItemStack fill = new ItemStack(Material.GRAY_STAINED_GLASS_PANE);
        for (int i = 0; i < 27; i++) gui.setItem(i, fill);
        List<String> cur = plugin.getConfig().getStringList("essence-recipe.grid");
        for (int i = 0; i < slots.length; i++) {
            if (i < cur.size() && !cur.get(i).equals("AIR")) gui.setItem(slots[i], new ItemStack(Material.valueOf(cur.get(i))));
            else gui.setItem(slots[i], null);
        }
        p.openInventory(gui);
    }

    @EventHandler
    public void onClose(InventoryCloseEvent e) {
        if (!e.getView().getTitle().equals(GUI_NAME)) return;
        List<String> list = new ArrayList<>();
        for (int s : slots) {
            ItemStack it = e.getInventory().getItem(s);
            list.add(it != null && it.getType() != Material.AIR ? it.getType().name() : "AIR");
        }
        plugin.getConfig().set("essence-recipe.grid", list);
        plugin.saveConfig();
        registerCurrentRecipe();
    }

    public void registerCurrentRecipe() {
        Bukkit.removeRecipe(recipeKey);
        List<String> grid = plugin.getConfig().getStringList("essence-recipe.grid");
        if (grid.isEmpty() || grid.stream().allMatch(s -> s.equals("AIR"))) return;
        ShapedRecipe recipe = new ShapedRecipe(recipeKey, plugin.createNovaEssence(1));
        recipe.shape("ABC", "DEF", "GHI");
        char[] chars = "ABCDEFGHI".toCharArray();
        for (int i = 0; i < 9; i++) {
            if (i < grid.size() && !grid.get(i).equals("AIR")) recipe.setIngredient(chars[i], Material.valueOf(grid.get(i)));
        }
        Bukkit.addRecipe(recipe);
    }
}''')

write_file(src + "listeners/PowerExecutionListener.java", '''package com.novasmp.listeners;

import com.novasmp.NovaSMP;
import com.novasmp.managers.BindManager;
import org.bukkit.*;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.player.*;
import org.bukkit.inventory.ItemStack;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.util.Vector;

import java.util.*;

public class PowerExecutionListener implements Listener {
    private final NovaSMP plugin;
    private final Map<UUID, Long> lastSneak = new HashMap<>();

    public PowerExecutionListener(NovaSMP plugin) { this.plugin = plugin; }

    private void dispatch(Player p, BindManager.TriggerType trigger) {
        if (plugin.isSafetyToggled(p)) return;
        int ess = plugin.getEssence(p);
        if (ess >= 5 && plugin.getBindManager().getPlayerBind(p, "supernova_domain") == trigger) executeDomain(p);
        else if (ess >= 5 && plugin.getBindManager().getPlayerBind(p, "supernova_pulse") == trigger) executePulse(p);
        else if (ess >= 4 && plugin.getBindManager().getPlayerBind(p, "supernova_repulsion") == trigger) executeRepulsion(p);
        else if (ess >= 3 && plugin.getBindManager().getPlayerBind(p, "constellation_step") == trigger) executeStep(p);
        else if (ess >= 2 && plugin.getBindManager().getPlayerBind(p, "stellar_leap") == trigger) executeLeap(p);
        else if (ess >= 2 && plugin.getBindManager().getPlayerBind(p, "thermo_smelt") == trigger) executeSmelt(p);
        else if (ess >= 1 && plugin.getBindManager().getPlayerBind(p, "merchants_favor") == trigger) executeFavor(p);
    }

    @EventHandler
    public void onSwap(PlayerSwapHandItemsEvent e) {
        if (e.getPlayer().isSneaking()) { e.setCancelled(true); dispatch(e.getPlayer(), BindManager.TriggerType.SNEAK_F); }
    }
    @EventHandler
    public void onDrop(PlayerDropItemEvent e) {
        if (e.getPlayer().isSneaking()) { e.setCancelled(true); dispatch(e.getPlayer(), BindManager.TriggerType.SNEAK_DROP); }
    }
    @EventHandler
    public void onInteract(PlayerInteractEvent e) {
        if (!e.getPlayer().isSneaking()) return;
        if (e.getAction() == Action.RIGHT_CLICK_AIR || e.getAction() == Action.RIGHT_CLICK_BLOCK) dispatch(e.getPlayer(), BindManager.TriggerType.SNEAK_RIGHT_CLICK);
        else if (e.getAction() == Action.LEFT_CLICK_AIR || e.getAction() == Action.LEFT_CLICK_BLOCK) dispatch(e.getPlayer(), BindManager.TriggerType.SNEAK_LEFT_CLICK);
    }
    @EventHandler
    public void onMove(PlayerMoveEvent e) {
        if (!e.getPlayer().isSneaking()) return;
        if (e.getTo() != null && e.getTo().getY() - e.getFrom().getY() > 0.38) dispatch(e.getPlayer(), BindManager.TriggerType.SNEAK_JUMP);
    }
    @EventHandler
    public void onSneak(PlayerToggleSneakEvent e) {
        if (!e.isSneaking()) return;
        UUID id = e.getPlayer().getUniqueId();
        long now = System.currentTimeMillis();
        if (lastSneak.containsKey(id) && now - lastSneak.get(id) < 350) dispatch(e.getPlayer(), BindManager.TriggerType.DOUBLE_SNEAK);
        lastSneak.put(id, now);
    }

    private void executeFavor(Player p) {
        if (plugin.getCooldownManager().isOnCooldown(p, "merchants_favor")) return;
        plugin.getCooldownManager().setCooldown(p, "merchants_favor", 300);
        p.addPotionEffect(new PotionEffect(PotionEffectType.HERO_OF_THE_VILLAGE, 1200, 4));
    }
    private void executeSmelt(Player p) {
        if (plugin.getCooldownManager().isOnCooldown(p, "thermo_smelt")) return;
        ItemStack it = p.getInventory().getItemInMainHand();
        Material res = switch (it.getType()) {
            case RAW_IRON -> Material.IRON_INGOT; case RAW_COPPER -> Material.COPPER_INGOT; case RAW_GOLD -> Material.GOLD_INGOT; case ANCIENT_DEBRIS -> Material.NETHERITE_SCRAP; case SAND -> Material.GLASS; default -> null;
        };
        if (res != null) {
            plugin.getCooldownManager().setCooldown(p, "thermo_smelt", 60);
            it.setType(res);
            p.playSound(p.getLocation(), Sound.BLOCK_FIRE_EXTINGUISH, 1.0f, 1.5f);
        }
    }
    private void executeLeap(Player p) {
        if (plugin.getCooldownManager().isOnCooldown(p, "stellar_leap")) return;
        plugin.getCooldownManager().setCooldown(p, "stellar_leap", 30);
        p.setVelocity(p.getLocation().getDirection().setY(0).normalize().multiply(1.3).setY(0.95));
        p.playSound(p.getLocation(), Sound.ENTITY_WIND_CHARGE_WIND_BURST, 1.5f, 1.2f);
    }
    private void executeStep(Player p) {
        if (plugin.getCooldownManager().isOnCooldown(p, "constellation_step")) return;
        plugin.getCooldownManager().setCooldown(p, "constellation_step", 60);
        Location target = p.getLocation().add(p.getLocation().getDirection().multiply(-4).setY(0));
        if (!target.getBlock().getType().isSolid()) p.teleport(target);
        p.playSound(p.getLocation(), Sound.ITEM_CHORUS_FRUIT_TELEPORT, 1.0f, 1.5f);
    }
    private void executeRepulsion(Player p) {
        if (plugin.getCooldownManager().isOnCooldown(p, "supernova_repulsion")) return;
        plugin.getCooldownManager().setCooldown(p, "supernova_repulsion", 90);
        for (Entity e : p.getNearbyEntities(4, 3, 4)) {
            if (e instanceof LivingEntity l && !e.equals(p)) l.setVelocity(l.getLocation().toVector().subtract(p.getLocation().toVector()).normalize().multiply(1.8).setY(0.4));
        }
    }
    private void executePulse(Player p) {
        if (plugin.getCooldownManager().isOnCooldown(p, "supernova_pulse")) return;
        plugin.getCooldownManager().setCooldown(p, "supernova_pulse", 120);
        for (Entity e : p.getNearbyEntities(3, 2, 3)) {
            if (e instanceof LivingEntity l && !e.equals(p)) {
                new BukkitRunnable() {
                    int t = 0;
                    @Override public void run() {
                        if (!l.isValid() || l.isDead() || t++ >= 3) { cancel(); return; }
                        l.setHealth(Math.max(0.0, l.getHealth() - 1.5));
                    }
                }.runTaskTimer(plugin, 0L, 20L);
            }
        }
    }
    private void executeDomain(Player p) {
        if (plugin.getCooldownManager().isOnCooldown(p, "supernova_domain")) return;
        List<Player> targets = new ArrayList<>(List.of(p));
        for (Entity e : p.getNearbyEntities(5, 5, 5)) if (e instanceof Player t) targets.add(t);
        plugin.getCooldownManager().setCooldown(p, "supernova_domain", 900);
        plugin.getDomainManager().startDomain(p, targets);
    }

    @EventHandler
    public void onCrit(EntityDamageByEntityEvent e) {
        if (e.getDamager() instanceof Player a && e.getEntity() instanceof LivingEntity v) {
            if (plugin.getEssence(a) >= 5 && a.getFallDistance() >= 3.0f) {
                v.setHealth(Math.max(0.0, v.getHealth() - 2.0));
                v.getWorld().playSound(v.getLocation(), Sound.BLOCK_ANVIL_LAND, 1.0f, 1.8f);
            }
        }
    }
}''')

write_file(src + "commands/BindsCommand.java", '''package com.novasmp.commands;
import com.novasmp.NovaSMP;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
public class BindsCommand implements CommandExecutor {
    private final NovaSMP plugin;
    public BindsCommand(NovaSMP p) { this.plugin = p; }
    @Override public boolean onCommand(CommandSender s, Command c, String l, String[] a) {
        if (s instanceof Player p) plugin.getBindManager().openGUI(p);
        return true;
    }
}''')

write_file(src + "commands/RecipeCommand.java", '''package com.novasmp.commands;
import com.novasmp.NovaSMP;
import com.novasmp.listeners.RecipeEditorListener;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
public class RecipeCommand implements CommandExecutor {
    private final NovaSMP plugin;
    public RecipeCommand(NovaSMP p) { this.plugin = p; }
    @Override public boolean onCommand(CommandSender s, Command c, String l, String[] a) {
        if (s instanceof Player p && p.hasPermission("nova.admin")) new RecipeEditorListener(plugin).openEditor(p);
        return true;
    }
}''')

write_file(src + "commands/IgniteCommand.java", '''package com.novasmp.commands;
import com.novasmp.NovaSMP;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
public class IgniteCommand implements CommandExecutor {
    private final NovaSMP plugin;
    public IgniteCommand(NovaSMP p) { this.plugin = p; }
    @Override public boolean onCommand(CommandSender s, Command c, String l, String[] a) {
        if (s instanceof Player p) {
            boolean cur = plugin.isIgnited(p);
            plugin.setIgnited(p, !cur);
            p.sendMessage(!cur ? "§e✦ Stellar core ignited!" : "§7Stellar illumination extinguished.");
        }
        return true;
    }
}''')

write_file(src + "commands/ToggleSafetyCommand.java", '''package com.novasmp.commands;
import com.novasmp.NovaSMP;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
public class ToggleSafetyCommand implements CommandExecutor {
    private final NovaSMP plugin;
    public ToggleSafetyCommand(NovaSMP p) { this.plugin = p; }
    @Override public boolean onCommand(CommandSender s, Command c, String l, String[] a) {
        if (s instanceof Player p) {
            boolean cur = plugin.isSafetyToggled(p);
            plugin.setSafetyToggled(p, !cur);
            p.sendMessage(!cur ? "§c[Safety Mode ON] §7Triggers disabled." : "§a[Safety Mode OFF] §7Triggers enabled.");
        }
        return true;
    }
}''')

print("[4/4] Project generation complete!")
