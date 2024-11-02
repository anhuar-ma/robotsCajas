
using Agents
using CairoMakie

@agent struct Robot(GridAgent{2,})
    type::String = "Robot"
    # direction[1] = 1 up , -1 down ; direction[2] ,1 = foward, -1 = backward
    direction::Vector{Int} = [1, 1]
    #limit , the first value is the first limit, the second the right limit
    limit::NTuple{2,Int} = (0, 0)

    # 90 is up, 270 is down, 0 is right, 180 is left
    looking_at::Int = 0

    move::Bool = false

    #0 significa no hay una caga, 1 significa que vamos a acomodar una caga y el 2
    #que estamos regresando a nuestra posición inical
    found_box::Int = 0

    #Past postiion para poder ir a dejar la caja y regresar a la posición anterior
    past_position::Vector{Int} = [-1, -1]
end

@agent struct Box(GridAgent{2})
    type::String = "Box"
end

@agent struct Estante(GridAgent{2})
    type::String = "Estante"
    cantidad_cajas::Int = 0
    movimientos_robots::Int = 0
end

function agent_step!(agent::Box, model)
    # print(agent.pos)
end
function agent_step!(agent::Estante, model)
    # print(agent.pos)
end

function agent_step!(agent::Robot, model)
    print(agent.pos)
    #Cada movimento voy a buscar la id del estante y le voy a sumar uno al contador
    agents_at_pos = agents_in_position((1, 1), model)
    estante_id = -1
    for agent_in_pos in agents_at_pos
        if agent_in_pos.type == "Estante"
            estante_id = agent_in_pos.id
            # println("---------------------------------")
        end
    end

    model[estante_id].movimientos_robots += 1

    if agent.found_box > 0

        #Si ya encontró la caja, entonces la lleva a la posición 49, 49
        if agent.found_box == 1
            if (agent.pos[1] < 50)
                agent.direction[1] = 1
                move_agent!(agent, (agent.pos[1] + 1, agent.pos[2]), model)


                #durante este trayecto hacia arriba, el robot va a estar viendo hacia arriba
                agent.looking_at = 90

            else

                #Se agrega caja a estante
                #se busca la id del estante
                agents_at_pos = agents_in_position((1, 1), model)
                estante_id = -1
                for agent_in_pos in agents_at_pos
                    if agent_in_pos.type == "Estante"
                        estante_id = agent_in_pos.id
                        # println("---------------------------------")
                    end
                end

                model[estante_id].cantidad_cajas += 1

                agent.found_box = 2

            end
        elseif agent.found_box == 2

            if (agent.pos[1] > agent.past_position[1])
                agent.direction[1] = -1
                #Si ya llegó a la posición 50 entonces regresa a la posición anterior

                move_agent!(agent, (agent.pos[1] - 1, agent.pos[2]), model)

                #durante este trayecto de regresar a su anterior posición, el robot va a estar viendo hacia abajo
                agent.looking_at = 270
            else
                agent.found_box = 0
                # agent.past_position = [-1, -1]
            end

        end


    else

        # randomwalk!(agent, model)
        # Determine the new position
        # y is 1 and x is 2

        #checking if is in the limits of y
        #if i'm going down and I have reach 1,the floor, then go up
        if (agent.pos[1] == 1 && agent.direction[1] == -1)
            agent.direction[1] = 1
            #if i'm going up and I have reach 50, then go down
        elseif (agent.pos[1] == 50 && agent.direction[1] == 1)
            agent.direction[1] = -1
        end

        #if is going up or down
        # direction_up_down = 0
        # if agent.move
        #     # println("algo")
        #     direction_up_down = 1
        #     agent.move = false
        # end

        agent.move = false
        #in direction the first is right or left, and the second is up or down
        new_pos = agent.pos
        #checking if is in the limits of x
        #if I have reach any limit then change direction
        if (agent.pos[2] == agent.limit[1] && agent.direction[2] == -1) || (agent.pos[2] == agent.limit[2] && agent.direction[2] == 1)
            agent.direction[2] *= -1
            agent.move = true

            #si llege al limite me voy a mover hacia arriba o hacia abajo

            if agent.direction[1] == 1
                agent.looking_at = 90
            else
                agent.looking_at = 270
            end

            new_pos = (agent.pos[1] + (1 * agent.direction[1]), agent.pos[2])
        else

            #si no estoy en el limite entonces me muevo hacia la dirección que estoy viendo

            if agent.direction[2] == 1
                agent.looking_at = 0
            else
                agent.looking_at = 180
            end

            new_pos = (agent.pos[1], agent.pos[2] + agent.direction[2])
        end

        # new_pos = (agent.pos[1] + (direction_up_down * agent.direction[1]), agent.pos[2] + agent.direction[2])
        # println(new_pos)
        # new_pos = (agent.pos[1], agent.pos[2] + agent.direction[1])


        #Verificar si hay una caja en la posición en la que estamos
        for box in nearby_agents(agent, model, 1)
            if box.type == "Box"
                println("Hay una caja en la posición: ", agent.pos)
                remove_agent!(box, model)
                agent.found_box = true
                agent.past_position = [agent.pos[1], agent.pos[2]]
            end
        end


        # Move the agent to the new position
        move_agent!(agent, new_pos, model)

    end

end

function initialize_model()
    # Se crea una grid de 50x50
    space = GridSpace((50, 50); periodic=false, metric=:manhattan)
    model = StandardABM(Union{Robot,Box,Estante}, space; agent_step!)
    #Se agregan los robots
    add_agent!(Robot, limit=(1, 10), direction=[1, -1], pos=(50, 1), model)
    add_agent!(Robot, limit=(11, 20), direction=[1, -1], pos=(50, 11), model)
    add_agent!(Robot, limit=(21, 30), direction=[1, -1], pos=(50, 21), model)
    add_agent!(Robot, limit=(31, 40), direction=[1, -1], pos=(50, 31), model)
    add_agent!(Robot, limit=(41, 50), direction=[1, -1], pos=(50, 41), model)

    # #Se agregan las cajas

    for i in 1:20
        add_agent!(Box, pos=(rand(1:50), rand(1:50)), model)
    end
    add_agent!(Box, pos=(50, 3), model)
    #Se agrega el estante teniendo la ultima id
    add_agent!(Estante, pos=(1, 1), model)
    # add_agent!(Box, pos=(1, 1), model)
    # add_agent!(Box, pos=(50, 1), model)
    return model
end

# model = initialize_model()
# a = add_agent!(Ghost, pos=(3, 3), model)