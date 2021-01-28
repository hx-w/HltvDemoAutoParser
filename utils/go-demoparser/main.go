package main

import (
	"fmt"
	"os"

	dem "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs"
	events "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs/events"
)

type UtilityRecord struct {
	thrower     string
	utType      string
	throw_pitch float32
	throw_yaw   float32
	throw_posX  float32
	throw_posY  float32
	throw_posZ  float32
	end_posX    float32
	end_posY    float32
	end_posZ    float32
	round       int
	valid       bool
}

var utrecord_collector map[int64]UtilityRecord

func main() {
	f, err := os.Open("demos/inferno.dem")
	if err != nil {
		panic(err)
	}
	defer f.Close()

	p := dem.NewParser(f)
	defer p.Close()

	round := 1

	// header, err := p.ParseHeader()
	// if err != nil {
	// 	panic(err)
	// }
	// mapname := header.MapName

	utrecord_collector = make(map[int64]UtilityRecord)
	p.RegisterEventHandler(func(e events.GrenadeProjectileThrow) {
		utrecord_collector[int64(e.Projectile.UniqueID())] = UtilityRecord{
			thrower:     string(e.Projectile.Thrower.Name),
			throw_yaw:   float32(e.Projectile.Thrower.ViewDirectionX()),
			throw_pitch: float32(e.Projectile.Thrower.ViewDirectionY()),
			throw_posX:  float32(e.Projectile.Thrower.LastAlivePosition.X),
			throw_posY:  float32(e.Projectile.Thrower.LastAlivePosition.Y),
			throw_posZ:  float32(e.Projectile.Thrower.LastAlivePosition.Z),
			utType:      string(e.Projectile.WeaponInstance.String()),
			round:       int(round),
			valid:       false,
		}
	})

	count := 0
	p.RegisterEventHandler(func(e events.GrenadeProjectileDestroy) {
		uId := int64(e.Projectile.UniqueID())
		utrecord, ok := utrecord_collector[uId]
		if ok && !utrecord.valid {
			utrecord.valid = true
			utrecord.end_posX = float32(e.Projectile.Position().X)
			utrecord.end_posY = float32(e.Projectile.Position().Y)
			utrecord.end_posZ = float32(e.Projectile.Position().Z)
			utrecord_collector[uId] = utrecord

			//

			// fmt.Printf("[%d] %s Throw %s IN round %d\n", count, utrecord.thrower, utrecord.utType, utrecord.round)
			count++

			fmt.Printf("[%s] setang %f %f 0; setpos %f %f %f\n", utrecord.utType, utrecord.throw_pitch, utrecord.throw_yaw, utrecord.throw_posX, utrecord.throw_posY, utrecord.throw_posZ)
			delete(utrecord_collector, uId)
		}
	})

	p.RegisterEventHandler(func(e events.RoundEnd) {
		round++
	})

	// Parse to end
	err = p.ParseToEnd()
	if err != nil {
		panic(err)
	}

}
