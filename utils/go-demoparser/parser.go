package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"time"

	dem "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs/common"
	events "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs/events"
)

type UtilityRecord struct {
	player_name      string
	steamid          uint64
	utType           string
	throw_pitch      float32
	throw_yaw        float32
	throw_posX       float32
	throw_posY       float32
	throw_posZ       float32
	end_posX         float32
	end_posY         float32
	end_posZ         float32
	round            int
	valid            bool
	start_time       time.Duration
	air_time         float32
	match_throw_time float32
}

var utrecord_collector map[int64]UtilityRecord
var type_map map[string]string
var matchId, demoId int
var matchName, matchTime, filePath, mapName string
var tickRate float64

func ArgParser() {
	flag.StringVar(&matchName, "matchname", "Unknown", "Demo match name")
	flag.StringVar(&matchTime, "matchtime", "2020-1-1 0:0:0", "Demo match time")
	flag.StringVar(&filePath, "filepath", "Unknown", "Demo file path")
	flag.IntVar(&matchId, "matchid", 0, "Demo match id")
	flag.IntVar(&demoId, "demoid", 0, "Demo id")

	flag.Parse()
}

func JsonFomat(ut UtilityRecord, round int) string {
	json_map := map[string]interface{}{
		"aim_pitch":        ut.throw_pitch,
		"aim_yaw":          ut.throw_yaw,
		"throw_x":          ut.throw_posX,
		"throw_y":          ut.throw_posY,
		"throw_z":          ut.throw_posZ,
		"end_x":            ut.end_posX,
		"end_y":            ut.end_posY,
		"end_z":            ut.end_posZ,
		"is_walk":          false,
		"is_jump":          false,
		"is_duck":          false,
		"is_left":          true,
		"is_right":         false,
		"map_belong":       mapName,
		"air_time":         ut.air_time,
		"match_id":         matchId,
		"match_round":      round,
		"match_name":       matchName,
		"match_time":       matchTime,
		"demo_id":          demoId,
		"steamid":          ut.steamid,
		"nickname":         ut.player_name,
		"tickrate":         tickRate,
		"utility_type":     type_map[ut.utType],
		"match_throw_time": ut.match_throw_time,
	}

	str, err := json.Marshal(json_map)
	if err != nil {
		panic(err)
	}
	return string(str)
}

func checkFileIsExist(filename string) bool {
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		return false
	}
	return true
}

func main() {
	const he_flash_time float32 = 1.63

	// arg info
	ArgParser()
	fmt.Println(matchName, matchTime, matchId, demoId)

	var infoPath = "static/info/" + matchName + ".txt"
	var infoFile *os.File
	var infoError error

	if !checkFileIsExist(infoPath) {
		infoFile, infoError = os.Create(infoPath)
	}
	infoFile, infoError = os.OpenFile(infoPath, os.O_WRONLY|os.O_APPEND, os.ModeAppend)
	if infoError != nil {
		panic(infoError)
	}
	defer infoFile.Close()

	// init
	infoFile.WriteString("[{}")

	f, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	p := dem.NewParser(f)
	defer p.Close()

	round := 0
	var round_start_time time.Duration

	header, err := p.ParseHeader()
	if err != nil {
		panic(err)
	}
	mapName = header.MapName
	tickRate = p.TickRate()
	count := 0

	type_map = make(map[string]string)
	type_map["Smoke Grenade"] = "smoke"
	type_map["HE Grenade"] = "grenade"
	type_map["Flashbang"] = "flash"
	type_map["Incendiary Grenade"] = "molotov"
	type_map["Molotov"] = "molotov"

	utrecord_collector = make(map[int64]UtilityRecord)

	p.RegisterEventHandler(func(e events.RoundStart) {
		round++
		round_start_time = p.CurrentTime()
	})

	p.RegisterEventHandler(func(e events.MatchStartedChanged) {
		round++
		round_start_time = p.CurrentTime()
	})

	p.RegisterEventHandler(func(e events.GrenadeProjectileThrow) {
		uId := int64(e.Projectile.WeaponInstance.UniqueID())
		utrecord, ok := utrecord_collector[uId]
		if !ok {
			utrecord_collector[int64(e.Projectile.WeaponInstance.UniqueID())] = UtilityRecord{
				player_name:      string(e.Projectile.Thrower.Name),
				steamid:          uint64(e.Projectile.Thrower.SteamID64),
				throw_yaw:        float32(e.Projectile.Thrower.ViewDirectionX()),
				throw_pitch:      float32(e.Projectile.Thrower.ViewDirectionY()),
				throw_posX:       float32(e.Projectile.Thrower.LastAlivePosition.X),
				throw_posY:       float32(e.Projectile.Thrower.LastAlivePosition.Y),
				throw_posZ:       float32(e.Projectile.Thrower.LastAlivePosition.Z),
				utType:           string(e.Projectile.WeaponInstance.String()),
				round:            int(round),
				valid:            false,
				start_time:       p.CurrentTime(),
				match_throw_time: float32((p.CurrentTime() - round_start_time).Seconds()),
			}
		} else {
			fmt.Println(utrecord.utType)
		}
	})

	// SMOKE DETONATE
	p.RegisterEventHandler(func(e events.SmokeStart) {
		uId := int64(e.Grenade.UniqueID())
		utrecord, ok := utrecord_collector[uId]
		if ok && !utrecord.valid {
			utrecord.valid = true
			utrecord.end_posX = float32(e.Position.X)
			utrecord.end_posY = float32(e.Position.Y)
			utrecord.end_posZ = float32(e.Position.Z)

			end_time := p.CurrentTime()
			utrecord.air_time = float32((end_time - utrecord.start_time).Seconds())
			count++

			json_str := JsonFomat(utrecord, round)
			n, infoError := io.WriteString(infoFile, ","+json_str)
			if infoError != nil {
				panic(infoError)
			}
			fmt.Printf("writen %d bytes | %d\n", n, count)

			utrecord_collector[uId] = utrecord
		}
	})

	// MOLOTOV & INC GRENADE DETONATE
	p.RegisterEventHandler(func(e events.GrenadeProjectileDestroy) {
		if e.Projectile.WeaponInstance.Type.String() != string("Incendiary Grenade") && e.Projectile.WeaponInstance.Type.String() != string("Molotov") {
			return
		}
		uId := int64(e.Projectile.WeaponInstance.UniqueID())

		utrecord, ok := utrecord_collector[uId]
		if ok && !utrecord.valid {
			utrecord.valid = true
			utrecord.end_posX = float32(e.Projectile.Position().X)
			utrecord.end_posY = float32(e.Projectile.Position().Y)
			utrecord.end_posZ = float32(e.Projectile.Position().Z)

			end_time := p.CurrentTime()
			utrecord.air_time = float32((end_time - utrecord.start_time).Seconds())
			count++

			json_str := JsonFomat(utrecord, round)
			n, infoError := io.WriteString(infoFile, ","+json_str)
			if infoError != nil {
				panic(infoError)
			}
			fmt.Printf("writen %d bytes | %d\n", n, count)
			utrecord_collector[uId] = utrecord
		}
	})

	// FLASH DETONATE
	p.RegisterEventHandler(func(e events.FlashExplode) {
		uId := int64(e.Grenade.UniqueID())
		utrecord, ok := utrecord_collector[uId]
		if ok && !utrecord.valid {
			utrecord.valid = true
			utrecord.end_posX = float32(e.Position.X)
			utrecord.end_posY = float32(e.Position.Y)
			utrecord.end_posZ = float32(e.Position.Z)
			utrecord.air_time = he_flash_time
			count++

			json_str := JsonFomat(utrecord, round)
			n, infoError := io.WriteString(infoFile, ","+json_str)
			if infoError != nil {
				panic(infoError)
			}
			fmt.Printf("writen %d bytes | %d\n", n, count)
			utrecord_collector[uId] = utrecord
		}
	})

	// HE GRENADE DETONATE
	p.RegisterEventHandler(func(e events.HeExplode) {
		uId := int64(e.Grenade.UniqueID())
		utrecord, ok := utrecord_collector[uId]
		if ok && !utrecord.valid {
			utrecord.valid = true
			utrecord.end_posX = float32(e.Position.X)
			utrecord.end_posY = float32(e.Position.Y)
			utrecord.end_posZ = float32(e.Position.Z)
			utrecord.air_time = he_flash_time
			count++
			json_str := JsonFomat(utrecord, round)
			n, infoError := io.WriteString(infoFile, ","+json_str)
			if infoError != nil {
				panic(infoError)
			}
			fmt.Printf("writen %d bytes | %d\n", n, count)

			utrecord_collector[uId] = utrecord
		}
	})

	p.RegisterEventHandler(func(e events.GamePhaseChanged) {
		if e.NewGamePhase == common.GamePhaseGameEnded {
			n, infoError := io.WriteString(infoFile, "]")
			if infoError != nil {
				panic(infoError)
			}
			fmt.Printf("writen %d bytes | %d\n", n, count)
		}
	})

	// Parse to end
	err = p.ParseToEnd()
	if err != nil {
		panic(err)
	}

}
