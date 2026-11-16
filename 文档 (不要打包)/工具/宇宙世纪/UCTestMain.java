import com.corrodinggames.librocket.scripts.ScriptEngine;
import com.corrodinggames.librocket.scripts.Debug;
import com.corrodinggames.rts.game.units.custom.j;
import com.corrodinggames.rts.game.units.custom.g;
import com.corrodinggames.rts.game.units.custom.logicBooleans.LogicBoolean;
import com.corrodinggames.rts.game.units.custom.logicBooleans.LogicBooleanLoader;
import com.corrodinggames.rts.game.units.custom.logicBooleans.VariableScope;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.nio.file.*;
import java.util.*;

/** Test-only bridge. It runs against an isolated Main + UC engine, never shipped as a unit. */
public class UCTestMain {
    static ScriptEngine scripts;
    static Debug debug;
    static j hq, core, factory;
    static int checks;
    static final String[] FACTIONS={"EFSF_0079","ZEON_0079","AEUG_0087","TITANS_0087","NEO_ZEON_0087","0093_EFSF","0093_NZN"};
    interface Job { void run() throws Exception; }
    interface Probe { boolean get() throws Exception; }

    static void onEngine(Job job) throws Exception {
        CountDownLatch done=new CountDownLatch(1);
        Throwable[] error={null};
        scripts.addRunnableToQueue(()->{
            try { job.run(); } catch(Throwable ex) { error[0]=ex; }
            finally {
                // The stock -nodisplay GUI attempts an extra repaint with no graphics context.
                try {
                    var field=com.corrodinggames.librocket.scripts.ScriptContext.class.getDeclaredField("libRocket");
                    field.setAccessible(true);
                    ((com.LibRocket)field.get(scripts.getRootNoCheck())).queueExtraUpdate=false;
                } catch(Exception ignored) {}
                done.countDown();
            }
        });
        if(!done.await(45,TimeUnit.SECONDS)) throw new Exception("Script queue timeout");
        if(error[0]!=null) throw new Exception(error[0]);
    }
    static void await(String label,long timeout,Probe probe) throws Exception {
        long until=System.currentTimeMillis()+timeout;
        while(System.currentTimeMillis()<until) {
            boolean[] ready={false};
            onEngine(()->ready[0]=probe.get());
            if(ready[0]) return;
            Thread.sleep(200);
        }
        onEngine(()->{
            if(!Arrays.asList(FACTIONS).contains(currentFaction())) {System.out.println("UC_DIAG PMC HQ="+hq.x.i()+" FactionIndex="+number(hq,"self.resource.FactionIndex"));return;}
            System.out.println("UC_DIAG active="+currentFaction()+" TP="+number(hq,"self.resource.TechPoint")+" auto="+number(hq,"memory.autoTech")+" coreAuto="+number(core,"memory.autoTech")+" pending="+condition(hq,"memory.ucAdvancePending")+" queue="+number(hq,"self.queueSize()")+" captured="+!condition(hq,"self.hasTags(includes='HQ_NotCaptured')"));
            j controller=reference(core,"self.attachment(slot='"+currentFaction()+"')");
            System.out.println("UC_DIAG controllerAuto="+number(controller,"memory.autoTech")+" activeTag="+condition(controller,"self.globalTeamTags(includes='"+currentFaction()+"')")+" age="+number(controller,"self.timeAlive"));
            for(String tech:technologies(currentFaction())) System.out.println("UC_DIAG tech "+tech+" done="+condition(hq,"self.globalTeamTags(includes='"+tech+"')")+" need="+number(controller,"memory."+tech+"_TechPoint"));
            if(label.contains("factory")) {
                for(String expr:new String[]{"self.timeAlive","memory.autoProduceCD","memory.canProduceBuildingList.size","self.resource.Mp","self.resource.MpMax","self.resource.Money","self.resource.Resource"}) System.out.println("UC_DIAG HQ "+expr+"="+number(hq,expr));
                System.out.println("UC_DIAG HQ AI="+condition(hq,"self.isControlledByAI()"));
                for(String expr:new String[]{"memory.buildDone","self.hasTags(includes='CanProduceBuilding')","self.globalTeamTags(includes='Unlock_RGM_79')"}) System.out.println("UC_DIAG factory "+expr+"="+condition(factory,expr));
                System.out.println("UC_DIAG factory age="+number(factory,"self.timeAlive"));
                for(String expr:new String[]{"self.resource.AIHard","self.resource.Mp","self.resource.MpMax","self.numberOfUnitsInTeam(withTag='RGM_89')","self.numberOfUnitsInTeam(withTag='RGM_86R_0093_EFSF')","self.numberOfUnitsInTeam(withTag='MSZ_006A1_0093_EFSF')","self.numberOfUnitsInTeam()"}) System.out.println("UC_DIAG factory "+expr+"="+number(factory,expr));
            }
        });
        throw new Exception("UC_ASSERT_FAIL timed out: "+label);
    }
    static void check(boolean condition,String label) {
        if(!condition) throw new RuntimeException("UC_ASSERT_FAIL "+label);
        checks++;
        System.out.println("UC_ASSERT_PASS "+label);
    }
    static float number(j unit,String expression) {return LogicBooleanLoader.parseBooleanBlock(unit.x,expression,false).readNumber(unit);}
    static j reference(j unit,String expression) {return (j)LogicBooleanLoader.parseBooleanBlock(unit.x,expression,false).readUnit(unit);}
    static boolean condition(j unit,String expression) {return LogicBoolean.create(unit.x,"if "+expression,null).read(unit);}
    static void action(j unit,String name) {
        var found=unit.x.h(name);
        if(found==null) throw new RuntimeException("Missing action "+unit.x.i()+":"+name);
        unit.a(found,(android.graphics.PointF)null,(com.corrodinggames.rts.game.units.am)null,0);
    }
    static void resource(j unit,String name,double value) {unit.x.j(name).a(unit,value);}
    static void memory(j unit,String values) {VariableScope.createMemoryWriter(values,unit.x,"UCVerify","memory").writeToUnit(unit);}
    static j create(String type,float x,float y,int team) {
        Long id=debug.createUnit(type,x,y,team,false);
        for(Object raw:com.corrodinggames.rts.game.units.am.bE) {
            var unit=(com.corrodinggames.rts.game.units.am)raw;
            if(unit.eh==id) return (j)unit;
        }
        throw new RuntimeException("Create failed "+type);
    }
    static String era(String faction) {return faction.startsWith("0093")?"0093":faction.endsWith("0087")?"0087":"0079";}
    static int eraIndex(String faction) {return era(faction).equals("0093")?2:era(faction).equals("0087")?1:0;}
    static List<String> technologies(String faction) throws Exception {return Files.readAllLines(Paths.get("../tech-"+faction+".txt"));}
    static float localEnd(String faction) throws Exception {return Float.parseFloat(Files.readString(Paths.get("../end-"+faction+".txt")).trim());}
    static float gate(String faction) throws Exception {return number(hq,"memory.ucEraTechBase")+localEnd(faction)+2700;}
    static String currentFaction() {
        for(String faction:FACTIONS) if(hq.x.i().equals("HQ_"+faction)||hq.x.i().equals("HQ_"+faction+"_Space")) return faction;
        return "UNKNOWN:"+hq.x.i();
    }
    static void setup(String faction,int tile,int team,int autoTech) {
        debug.removeAllUnits();
        for(int i=0;i<2;i++) com.corrodinggames.rts.game.n.k(i).a(g.a(""));
        // An out-of-range enemy HQ keeps the skirmish alive without interfering with test units.
        j opponent=create("HQ_EFSF_0079",200000,200000,1-team);
        resource(opponent,"FactionIndex",0);resource(opponent,"GameStart",0);
        resource(opponent,"Money",0);resource(opponent,"Resource",0);resource(opponent,"TechPoint",0);
        memory(opponent,"techX=0,resX=0");
        hq=create("HQ_VS_GE_UC"+era(faction),300,300,team);
        memory(hq,"resX=1,mpX=1,mpStart=10000,techX=0,techLimit=3,autoTech="+autoTech+",techShare=0,allowACEUnit=1,gameStartChangeFaction=false,readyOK=true,stageIndex="+(eraIndex(faction)==0?1001:eraIndex(faction)==1?1010:1020));
        resource(hq,"GameStart",0);resource(hq,"FactionIndex",0);resource(hq,"tileMode",tile);
        resource(hq,"Money",5000000);resource(hq,"Resource",5000000);resource(hq,"MpMax",10000);
        resource(hq,"TechPoint",0);resource(hq,"AIHard",1);
        action(hq,"ChoseFaction_"+faction);
        resource(hq,"GameStart",1);
    }
    static void checkEra(String faction,int pages) throws Exception {
        check(currentFaction().equals(faction),"HQ "+faction);
        check(condition(hq,"self.globalTeamTags(includes='"+faction+"')"),"active faction tag "+faction);
        core=reference(hq,"self.attachment(slot='TechTreeMarkerSlot')");
        check(core!=null&&core.x.i().equals("TechTree_Core_UC"),"UC core slot");
        check(number(core,"memory.ucPages")==pages,"page count "+pages);
        j controller=reference(core,"self.attachment(slot='"+faction+"')");
        check(controller!=null,"controller "+faction);
        check(condition(hq,"self.globalTeamTags(includes='Tech_"+faction+"_BaseTech')"),"base research "+faction);
        String last=technologies(faction).get(technologies(faction).size()-1);
        float expected=number(hq,"memory.ucEraTechBase")+localEnd(faction);
        check(number(controller,"memory."+last+"_TechPoint")==expected,"cumulative technology threshold "+faction);
    }
    static boolean allResearch(String faction) throws Exception {
        for(String tech:technologies(faction)) if(!condition(hq,"self.globalTeamTags(includes='"+tech+"')")) return false;
        return true;
    }
    static void complete(String faction) throws Exception {
        j controller=reference(core,"self.attachment(slot='"+faction+"')");
        for(String tech:technologies(faction)) {
            action(controller,tech+"_Done");
            check(condition(hq,"self.globalTeamTags(includes='"+tech+"')"),"research "+tech);
        }
    }
    static void advance(String from,String to) throws Exception {
        float required=gate(from);
        String name="UC_Advance_"+from+"_To_"+to;
        resource(hq,"TechPoint",required-2700);
        action(hq,name);
        check(currentFaction().equals(from),"research completion alone cannot advance");
        resource(hq,"TechPoint",required-1);
        action(hq,name);
        check(currentFaction().equals(from),"TP gate lower boundary");
        float money=number(hq,"self.resource.Money"),materials=number(hq,"self.resource.Resource");
        resource(hq,"TechPoint",required);
        action(hq,name);
        check(currentFaction().equals(to),"TP gate exact boundary");
        check(number(hq,"self.resource.TechPoint")==required,"TP retained");
        check(number(hq,"memory.ucEraTechBase")==required,"next era offset");
        check(number(hq,"self.resource.Money")==money&&number(hq,"self.resource.Resource")==materials,"economy retained");
    }
    static void entryTests() throws Exception {
        for(int tile=0;tile<2;tile++) for(String faction:FACTIONS) {
            final int terrain=tile;
            onEngine(()->setup(faction,terrain,0,0));Thread.sleep(1800);
            onEngine(()->{
                checkEra(faction,1);
                check(number(core,"memory.ucStartEra")==eraIndex(faction),"initial era "+faction);
                check(number(core,"memory.ucPage")==0,"start on first page");
                action(core,"ShowTechTree_UC");
            });Thread.sleep(400);
            onEngine(()->{
                j controller=reference(core,"self.attachment(slot='"+faction+"')");
                check(reference(controller,"self.attachment(slot='Page')")!=null,"starting technology page opens");
            });
            System.out.println("UC_ENTRY_PASS "+terrain+" "+faction);
        }
    }
    static void routeTests() throws Exception {
        String[][] routes={{"EFSF_0079","AEUG_0087","0093_EFSF"},{"EFSF_0079","TITANS_0087","0093_NZN"},{"EFSF_0079","TITANS_0087","0093_EFSF"},{"ZEON_0079","AEUG_0087","0093_EFSF"},{"ZEON_0079","NEO_ZEON_0087","0093_NZN"}};
        for(int tile=0;tile<2;tile++) for(String[] route:routes) {
            final int terrain=tile;
            final String category=tile==0?"_Land":"_Space";
            onEngine(()->setup(route[0],terrain,0,0));Thread.sleep(1800);
            onEngine(()->{checkEra(route[0],1);action(core,"ShowTechTree_UC");factory=create("Factory_"+route[0]+category,500,500,0);complete(route[0]);});Thread.sleep(500);
            j[] saved={core};
            onEngine(()->advance(route[0],route[1]));Thread.sleep(1800);
            onEngine(()->{checkEra(route[1],2);check(condition(core,"not memory.showTechTree"),"research button returns after era change");check(core==saved[0],"core identity retained");check(factory.x.i().equals("Factory_"+route[1]+category),"factory advances "+route[1]);complete(route[1]);});Thread.sleep(500);
            onEngine(()->advance(route[1],route[2]));Thread.sleep(1800);
            onEngine(()->{checkEra(route[2],3);check(core==saved[0],"final core identity");check(factory.x.i().equals("Factory_"+route[2]+category),"factory advances "+route[2]);action(core,"ShowTechTree_UC");});Thread.sleep(400);
            onEngine(()->{j controller=reference(core,"self.attachment(slot='"+route[2]+"')");action(reference(controller,"self.attachment(slot='Page')"),"LastPage");});Thread.sleep(500);
            onEngine(()->{checkSinglePage(route[1]);check(number(core,"memory.ucPage")==1,"history page selected");j controller=reference(core,"self.attachment(slot='"+route[1]+"')");check(reference(controller,"self.attachment(slot='Page')")!=null,"history page opens");});
            System.out.println("UC_ROUTE_PASS "+terrain+" "+String.join(" -> ",route));
        }
    }
    static int combatCount() {
        int count=0;
        for(Object raw:com.corrodinggames.rts.game.units.am.bE) {
            var unit=(com.corrodinggames.rts.game.units.am)raw;
            if(unit.bX==hq.bX&&unit instanceof j&&condition((j)unit,"self.hasTags(includes='Unit')")) count++;
        }
        return count;
    }
    static boolean hasProductionQueue() {
        for(Object raw:com.corrodinggames.rts.game.units.am.bE) {
            var unit=(com.corrodinggames.rts.game.units.am)raw;
            if(unit.bX==hq.bX&&unit instanceof j&&((j)unit).x.i().startsWith("Factory_")&&number((j)unit,"self.queueSize()")>0) return true;
        }
        return false;
    }
    static void factoryTest(String faction,int team) throws Exception {
        // HQ dispatches production randomly across its buildings; observe all of its factories.
        onEngine(()->factory=create("Factory_"+faction+"_Land",500,500,team));Thread.sleep(500);
        onEngine(()->{memory(factory,"buildDone=true");action(factory,"Building_GetDone");});
        int[] initial={0};
        onEngine(()->initial[0]=combatCount());
        await("AI factory queue "+faction,60000,()->hasProductionQueue());
        await("AI factory output "+faction,60000,()->combatCount()>initial[0]);
        onEngine(()->check(true,"AI produces units "+faction));
    }
    static void aiTest(String faction,int autoTech,boolean fullRoute) throws Exception {
        // A fresh skirmish resets the native AI and team caches between faction cases.
        // Debug.removeAllUnits alone preserves AI planning state from earlier cases.
        onEngine(()->scripts.getRootNoCheck().startNew("maps/skirmish/[p2]Big Island (2p).tmx"));Thread.sleep(1200);
        onEngine(()->{debug.overrideDeltaSpeed(6);setup(faction,0,1,autoTech);});Thread.sleep(1200);
        onEngine(()->{checkEra(faction,1);resource(hq,"TechPoint",localEnd(faction)+1);});
        await("AI researches "+faction,autoTech==0?100000:12000,()->allResearch(faction));
        onEngine(()->{check(allResearch(faction),"AI researches "+faction+" auto="+autoTech);check(currentFaction().equals(faction),"AI waits for era TP");});
        factoryTest(faction,1);
        if(fullRoute) {
            String current=faction;
            int pages=1;
            while(!current.startsWith("0093")) {
                final String previous=current;
                float[] required={0};
                onEngine(()->{required[0]=gate(previous);resource(hq,"TechPoint",required[0]-1);});Thread.sleep(300);
                onEngine(()->{check(currentFaction().equals(previous),"AI cannot cross TP gate early");resource(hq,"TechPoint",required[0]);});
                await("AI advances "+previous,10000,()->!currentFaction().equals(previous));
                String[] next={null};
                onEngine(()->next[0]=currentFaction());
                current=next[0];pages++;
                final String target=current;
                final int count=pages;
                Thread.sleep(700);
                onEngine(()->{
                    checkEra(target,count);
                    boolean allowed=previous.equals("EFSF_0079")?(target.equals("AEUG_0087")||target.equals("TITANS_0087")):previous.equals("ZEON_0079")?(target.equals("AEUG_0087")||target.equals("NEO_ZEON_0087")):previous.equals("TITANS_0087")?(target.equals("0093_EFSF")||target.equals("0093_NZN")):previous.equals("AEUG_0087")?target.equals("0093_EFSF"):target.equals("0093_NZN");
                    check(allowed,"AI random faction is allowed");
                    check(number(hq,"self.resource.TechPoint")==required[0],"AI retains cumulative TP");
                    resource(hq,"TechPoint",number(hq,"memory.ucEraTechBase")+localEnd(target)+1);
                });
                await("AI researches next era "+target,12000,()->allResearch(target));
                System.out.println("UC_AI_ADVANCE_PASS "+previous+" -> "+target);
            }
        }
        System.out.println("UC_AI_PASS "+faction+" auto="+autoTech);
    }
    static int unitFamilyCount(String prefix) {
        int count=0;
        for(Object raw:com.corrodinggames.rts.game.units.am.bE) {
            var unit=(com.corrodinggames.rts.game.units.am)raw;
            if(unit.bX==hq.bX&&unit instanceof j) {
                String name=((j)unit).x.i();
                if(name.equals(prefix)||name.startsWith(prefix+"_")) count++;
            }
        }
        return count;
    }
    static void technologyMergeTests() throws Exception {
        List<String[]> cases=new ArrayList<>(),production=new ArrayList<>();
        for(String line:Files.readAllLines(Paths.get("../tech-merge-cases.txt"))) cases.add(line.split("\\t"));
        for(String line:Files.readAllLines(Paths.get("../tech-merge-production.txt"))) production.add(line.split("\\t"));
        onEngine(()->{
            debug.overrideDeltaSpeed(30);
            for(Object raw:com.corrodinggames.rts.game.units.custom.l.d) {
                String name=((com.corrodinggames.rts.game.units.custom.l)raw).i();
                check(!name.equals("MS_15A")&&!name.equals("EMS_10F")&&!name.equals("Tech_ZEON_0079_T2_GyanPowerfulPlan"),"removed unit absent "+name);
            }
        });
        for(String faction:FACTIONS) {
            if(faction.startsWith("0093")) continue;
            for(int tile=0;tile<2;tile++) {
                final int terrain=tile;
                onEngine(()->setup(faction,terrain,0,0));Thread.sleep(1200);
                onEngine(()->{
                    checkEra(faction,1);
                    j controller=reference(core,"self.attachment(slot='"+faction+"')");
                    for(String tech:technologies(faction)) {
                        for(String[] row:cases) if(row[0].equals(faction)&&row[1].equals(tech))
                            for(String unit:row[2].split(",")) check(!condition(hq,"self.globalTeamTags(includes='Unlock_"+unit+"')"),"locked before "+tech+" "+unit);
                        action(controller,tech+"_Done");
                    }
                });Thread.sleep(500);
                onEngine(()->{
                    for(String[] row:cases) if(row[0].equals(faction)) {
                        for(String unit:row[2].split(",")) check(condition(hq,"self.globalTeamTags(includes='Unlock_"+unit+"')"),"unlocked after "+row[1]+" "+unit);
                        System.out.println("UC_TECH_MERGE_PASS "+terrain+" "+row[1]);
                    }
                });
                List<String[]> batch=new ArrayList<>();List<j> factories=new ArrayList<>();
                for(String[] row:production) if(row[0].equals(faction)&&Integer.parseInt(row[1])==terrain) batch.add(row);
                onEngine(()->{
                    for(int i=0;i<batch.size();i++) factories.add(create(batch.get(i)[4],500+i*24,600,0));
                });Thread.sleep(300);
                int[] before=new int[batch.size()];
                onEngine(()->{
                    for(int i=0;i<batch.size();i++) {
                        j building=factories.get(i);String[] row=batch.get(i);
                        memory(building,"buildDone=true");action(building,"Building_GetDone");
                        before[i]=unitFamilyCount(row[3]);
                        if(building.x.h("Pannel_"+row[3])!=null) action(building,"Pannel_"+row[3]);
                        var button=building.x.h(row[5]);check(button!=null,"production action "+row[4]+" "+row[5]);
                        building.a(button,false,(android.graphics.PointF)null,(com.corrodinggames.rts.game.units.am)null);
                        check(number(building,"self.queueSize()")>0,"queued production "+row[3]);
                    }
                });
                await("merged factory output "+faction+" "+terrain,60000,()->{
                    for(int i=0;i<batch.size();i++) if(unitFamilyCount(batch.get(i)[3])<=before[i])return false;
                    return true;
                });
                onEngine(()->{
                    for(String[] row:batch) {check(true,"factory produced "+row[3]);System.out.println("UC_PRODUCTION_PASS "+terrain+" "+row[4]+" "+row[3]);}
                });
            }
        }
        List<j> bodies=new ArrayList<>();
        onEngine(()->{
            for(String name:Files.readAllLines(Paths.get("../tech-merge-forms.txt"))) bodies.add(create(name,900,900,0));
        });Thread.sleep(1000);
        onEngine(()->{
            for(j body:bodies) {check(body.cu>0,"form initializes alive "+body.x.i());System.out.println("UC_FORM_PASS "+body.x.i());}
            debug.overrideDeltaSpeed(-1);
        });
    }
    static void pmcTests() throws Exception {
        onEngine(()->scripts.getRootNoCheck().startNew("maps/skirmish/[p4]Desert (4p).tmx"));Thread.sleep(1200);
        for(int tile=0;tile<2;tile++) for(String year:new String[]{"0079","0087","0093"}) {
            final int terrain=tile;
            final int[] savedAlly={0};
            onEngine(()->{
                debug.removeAllUnits();
                var own=com.corrodinggames.rts.game.n.k(0);
                var other=com.corrodinggames.rts.game.n.k(1);
                var enemy=com.corrodinggames.rts.game.n.k(2);enemy.r=own.r+2;
                j hostile=create("HQ_EFSF_0079",200000,200000,2);
                resource(hostile,"GameStart",0);resource(hostile,"Money",0);resource(hostile,"Resource",0);
                memory(hostile,"resX=0,techX=0");
                own.a(g.a(""));other.a(g.a(""));savedAlly[0]=other.r;other.r=own.r+1;
                j ally=create("HQ_EFSF_0079",1300,1300,1);
                resource(ally,"GameStart",0);resource(ally,"Money",0);resource(ally,"Resource",0);
                memory(ally,"resX=0,techX=0");
                hq=create("HQ_VS_GE_UC"+year,300,300,0);
                memory(hq,"gameReady=true,readyOK=false,gameStartChangeFaction=false,resX=1,mpX=1,mpStart=60,techX=0,autoTech=0,techShare=0");
                resource(hq,"GameStart",0);resource(hq,"FactionIndex",0);resource(hq,"tileMode",terrain);
                resource(hq,"Money",500000);resource(hq,"Resource",500000);
                check(hq.x.h("ChoseFaction_PMC")!=null,"PMC action exists "+year);
                action(hq,"ChoseFaction_PMC");
                check(number(hq,"self.resource.FactionIndex")==0,"PMC rejected without allied player "+year);
                other.r=own.r;
            });Thread.sleep(400);
            onEngine(()->{
                check(number(hq,"self.numberOfUnitsInAllyNotOwnTeam(withTag='HQ')")>0,"PMC ally recognized");
                action(hq,"ChoseFaction_PMC");
                check(number(hq,"self.resource.FactionIndex")==9900101,"PMC can be selected "+year);
                resource(hq,"GameStart",1);
            });
            await("PMC HQ "+year,5000,()->hq.x.i().equals("HQ_PMC"));
            await("PMC slots "+year,5000,()->number(hq,"self.numberOfUnitsInTeam(withTag='PMC_Slot')")==4);
            onEngine(()->{
                check(condition(hq,"self.hasTags(includes='PMC')"),"PMC tag retained");
                core=reference(hq,"self.attachment(slot='TechTreeMarkerSlot')");
                check(core!=null&&core.x.i().equals("TechTree_Core_PMC"),"independent PMC tech core");
                check(combatCount()==0,"PMC has no starting combat units");
                check(hq.x.h("PMC_Borrow")!=null,"PMC borrow action exposed");
                check(hq.x.h("PMC_BuyCqb")!=null,"PMC upgrade action exposed");
                action(core,"ShowTechTree_PMC");
            });Thread.sleep(400);
            onEngine(()->{
                j controller=reference(core,"self.attachment(slot='PMC')");
                j page=reference(controller,"self.attachment(slot='Page')");
                check(page!=null&&page.x.i().equals("TechTree_UI_Page_PMC_00"),"PMC placeholder page opens");
                System.out.println("UC_PMC_PASS "+terrain+" "+year);
            });
            if(terrain==1&&year.equals("0093")) {
                final j[] borrowed={null};
                onEngine(()->{
                    borrowed[0]=create("RGM_89",800,800,1);
                    resource(borrowed[0],"PilotType",1101);
                });
                await("PMC allied pilot initializes",5000,()->condition(borrowed[0],"memory.battleUnitCore.hp>0 and memory.pilotUnit.hp>0 and memory.pilotUnit.parent==self"));
                // The five-argument engine entry sets thisActionTarget for ground clicks.
                onEngine(()->hq.a(hq.x.h("PMC_Borrow"),new android.graphics.PointF(number(borrowed[0],"self.x"),number(borrowed[0],"self.y")),null,0,0));
                onEngine(()->{
                    System.out.println("UC_PMC_DIAG candidate="+(reference(hq,"memory.pmcBorrowCandidate")==borrowed[0])+" team="+number(borrowed[0],"self.teamId")+" borrow="+condition(borrowed[0],"memory.pmcBorrowActive")+" control="+condition(borrowed[0],"memory.manualControlEnabled")+" slot="+(reference(hq,"memory.manualControlledUnit")==borrowed[0])+" close="+condition(borrowed[0],"memory.close")+" captured="+!condition(hq,"self.hasTags(includes='HQ_NotCaptured')"));
                });
                await("PMC borrow grant",5000,()->borrowed[0].bX==hq.bX&&condition(borrowed[0],"memory.manualControlEnabled and memory.pmcBorrowActive"));
                onEngine(()->{
                    check(reference(hq,"memory.manualControlledUnit")==borrowed[0],"PMC owns single control slot");
                });
                final j[] site={null};
                onEngine(()->{
                    j ally=reference(borrowed[0],"memory.pmcOriginalHQ");
                    resource(ally,"FactionIndex",1030101);resource(ally,"GameStart",1);
                    com.corrodinggames.rts.game.n.k(1).b(g.a("0093_EFSF,Tech_0093_EFSF_BaseTech"));
                    site[0]=create("StrategicLocation_0093",800,800,-2);
                });Thread.sleep(700);
                onEngine(()->{
                    memory(site[0],"captureTimer=0,nearestUnit=customTarget1");
                    // Find the borrowed MS via the stock capture scan, then complete capture.
                    action(site[0],"CheckNearestUnit");action(site[0],"CheckCaptureBarZero");
                });
                await("PMC capture handed to original ally",5000,()->site[0].bX==com.corrodinggames.rts.game.n.k(1));
                await("PMC capture has allied building slots",5000,()->{
                    j slot=reference(site[0],"self.attachment(slot='BuildingSlot_1')");
                    return slot!=null&&slot.x.i().equals("0093_BuildingSlot");
                });
                onEngine(()->{
                    check(!condition(site[0],"self.hasTags(includes='PMC')"),"captured site is not PMC restricted");
                    check(number(site[0],"self.resource.FactionIndex")==1030101,"captured site uses ally faction");
                    for(int slot=1;slot<=4;slot++)check(reference(site[0],"self.attachment(slot='BuildingSlot_"+slot+"')")!=null,"allied capture slot "+slot);
                    com.corrodinggames.rts.game.n.k(1).b(g.a("Unlock_Refinery_Common_T3"));
                    resource(site[0],"Money",5000);resource(site[0],"Resource",5000);
                    j slot=reference(site[0],"self.attachment(slot='BuildingSlot_1')");
                    var button=slot.x.h("Build_Refinery_Common_T3");check(button!=null,"captured slot has refinery action");
                    slot.a(button,false,(android.graphics.PointF)null,(com.corrodinggames.rts.game.units.am)null);
                    check(number(slot,"self.queueSize()")>0,"captured slot accepts construction queue");
                });
                await("PMC captured slot builds allied refinery",10000,()->{
                    j slot=reference(site[0],"self.attachment(slot='BuildingSlot_1')");
                    j building=reference(slot,"self.attachment(slot='Building')");
                    return building!=null&&building.x.i().equals("Refinery_Common_T3")&&building.bX==com.corrodinggames.rts.game.n.k(1);
                });
                onEngine(()->{
                    action(borrowed[0],"ManualControl_Release");
                });
                await("PMC returns borrowed unit",5000,()->borrowed[0].bX==com.corrodinggames.rts.game.n.k(1)&&!condition(borrowed[0],"memory.manualControlEnabled or memory.pmcBorrowActive"));
                System.out.println("UC_PMC_BORROW_PASS");
            }
            onEngine(()->com.corrodinggames.rts.game.n.k(1).r=savedAlly[0]);
        }
        onEngine(()->scripts.getRootNoCheck().startNew("maps/skirmish/[p2]Big Island (2p).tmx"));Thread.sleep(1200);
    }
    static void aceTests() throws Exception {
        onEngine(()->setup("AEUG_0087",0,0,0));Thread.sleep(1800);
        // Keep an earlier-era tag too: ACE selection must follow PilotType, not tag order.
        onEngine(()->{core=reference(hq,"self.attachment(slot='TechTreeMarkerSlot')");hq.bX.b(g.a("EFSF_0079"));});
        for(String row:Files.readAllLines(Paths.get("../ace-cases.tsv"))) {
            String[] fields=row.split("\t");final j[] body={null};
            onEngine(()->{
                body[0]=create("RGM_79",900,900,0);
                resource(body[0],"PilotCustom",2);resource(body[0],"PilotType",Integer.parseInt(fields[1]));
            });
            Thread.sleep(1800);
            onEngine(()->{
                j pilot=reference(body[0],"self.attachment(slot='Pilot')");
                System.out.println("UC_ACE_DIAG wanted="+fields[0]+" type="+number(body[0],"self.resource.PilotType")+" custom="+number(body[0],"self.resource.PilotCustom")+" pilot="+(pilot==null?"null":pilot.x.i())+" bodyPilot="+(reference(body[0],"memory.pilotUnit")==pilot));
                if(pilot!=null)System.out.println("UC_ACE_DIAG target="+(reference(pilot,"customTarget1")==body[0])+" core="+(reference(pilot,"self.attachment(slot='BattleUnitCore')")!=null));
            });
            await("ACE converts "+fields[0],10000,()->{
                j pilot=reference(body[0],"memory.pilotUnit");
                return pilot!=null&&pilot.x.i().equals(fields[0])&&number(pilot,"self.hp")>0;
            });
            onEngine(()->{
                j pilot=reference(body[0],"memory.pilotUnit");
                check(pilot.x.i().equals(fields[0]),"ACE concrete identity "+fields[0]);
                check(number(pilot,"memory.baseShootLevel")>0,"ACE initialized stats "+fields[0]);
            });
            System.out.println("UC_ACE_PASS "+fields[0]);
        }
    }
    static void checkSinglePage(String selected) {
        int count=0;
        for(String faction:FACTIONS) {
            j controller=reference(core,"self.attachment(slot='"+faction+"')");
            if(controller==null)continue;
            j page=reference(controller,"self.attachment(slot='Page')");
            if(page!=null&&page.cu>0) {
                count++;check(faction.equals(selected),"no stale page "+faction);
            }
        }
        check(count==1,"exactly one visible technology page");
    }
    static void tests() throws Exception {
        scripts=ScriptEngine.getInstance();
        var constructor=Debug.class.getDeclaredConstructor(com.corrodinggames.librocket.scripts.Root.class);
        constructor.setAccessible(true);debug=constructor.newInstance(scripts.getRootNoCheck());scripts.setupScriptContext(debug);
        onEngine(()->scripts.getRootNoCheck().startNew("maps/skirmish/[p2]Big Island (2p).tmx"));Thread.sleep(1200);
        System.out.println("UC_UNIT_COUNT "+com.corrodinggames.rts.game.units.custom.l.d.size());
        check(com.corrodinggames.rts.game.units.custom.l.d.size()<3000,"loaded unit count below 3000");
        if(Boolean.getBoolean("uc.aceOnly")) {aceTests();System.out.println("UC_RUNTIME_SUCCESS checks="+checks);return;}
        if(Boolean.getBoolean("uc.techMergeOnly")) {technologyMergeTests();System.out.println("UC_RUNTIME_SUCCESS checks="+checks);return;}
        if(Boolean.getBoolean("uc.pmcOnly")) {pmcTests();System.out.println("UC_RUNTIME_SUCCESS checks="+checks);return;}
        if(!Boolean.getBoolean("uc.aiOnly")) {pmcTests();aceTests();entryTests();routeTests();}
        for(String faction:FACTIONS) if(System.getProperty("uc.aiFaction",faction).equals(faction)) aiTest(faction,1,!faction.startsWith("0093"));
        if(System.getProperty("uc.aiFaction")==null) {aiTest("EFSF_0079",0,false);aiTest("AEUG_0087",0,false);}
        onEngine(()->debug.overrideDeltaSpeed(-1));
        System.out.println("UC_RUNTIME_SUCCESS checks="+checks);
    }
    public static void main(String[] arguments) {
        new Thread(()->{
            try {
                Path log=Paths.get("runtime.log");long until=System.currentTimeMillis()+240000;
                while(System.currentTimeMillis()<until) {
                    if(Files.exists(log)&&Files.readString(log).contains("Init completed")&&ScriptEngine.getInstance()!=null) break;
                    Thread.sleep(250);
                }
                tests();System.exit(0);
            } catch(Throwable error) {error.printStackTrace();System.out.println("UC_RUNTIME_FAILURE "+error);System.exit(7);}
        },"UC-validation").start();
        com.corrodinggames.rts.java.Main.main(arguments);
    }
}
