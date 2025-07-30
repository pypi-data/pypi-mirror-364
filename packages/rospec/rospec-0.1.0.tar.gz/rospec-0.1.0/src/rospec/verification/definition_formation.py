import copy
from typing import Union

from rospec.language.nodes import (
    ROSpecNode,
    TypeAlias,
    MessageAlias,
    PolicyInstance,
    NodeType,
    NodeInstance,
    PluginType,
    PluginInstance,
    System,
    Program,
    Publisher,
    Subscriber,
    Service,
    Action,
    TFTransform,
    Connection,
    ServiceActionRole,
    TransformType,
    Literal,
)
from rospec.language.ttypes import (
    StructType,
    BasicType,
    TType,
    RefinedType,
    OptionalType,
    NodeT,
    t_bottom,
    EnumType,
    PluginT,
)
from rospec.verification.context import Context
from rospec.verification.interpreter import interpret, interpret_connection
from rospec.verification.statement_formation import st_formation
from rospec.verification.substitution import (
    substitute_connection_with_assignments,
    substitute_connection_with_remaps,
    selfification,
    inverse_expr_substitution_in_type,
)
from rospec.verification.subtyping import is_subtype
from rospec.verification.type_formation import ty_formation
from rospec.verification.utils import convert_to_expression, check_policies
from rospec import errors


def d_type_alias(context: Context, ty_alias: TypeAlias) -> Context:
    ty_formation(context, ty_alias.old_ttype)
    if isinstance(ty_alias.old_ttype, EnumType):
        pass
        # for enum in ty_alias.old_ttype.ttypes:
        #    context = context.add_enum(enum.name, enum.name)
    return context.add_alias(ty_alias.new_ttype, ty_alias.old_ttype)


def d_message_alias(context: Context, msg_alias: MessageAlias) -> Context:
    ty_formation(context, msg_alias.old_ttype)
    old_ty_struct = context.get_alias(msg_alias.old_ttype)

    # Ensure that the types are correct
    assert isinstance(old_ty_struct, StructType)
    assert isinstance(msg_alias.new_ttype, BasicType)

    # Ensure that the set of fields in msg_alias.fields is exactly the same as the set of fields in old_ty_struct
    for field in msg_alias.fields:
        if field.identifier.name not in old_ty_struct.fields:
            context = context.add_error(
                errors.MESSAGE_FIELD_ERROR.format(
                    field=field.identifier.name, ttype=field.ttype, expected_type=msg_alias.old_ttype
                )
            )
        else:
            field_ttype = old_ty_struct.fields[field.identifier.name]
            if not is_subtype(context, field.ttype, field_ttype):
                context = context.add_error(
                    errors.MESSAGE_FIELD_NOT_SUBTYPE.format(
                        field=field.identifier.name, ttype=field.ttype, expected_type=field_ttype
                    )
                )

    # TODO: The dependencies can only be checked at execution time, that is for future work.

    # Create the new struct type and add it to the context
    new_ty_struct = StructType({f.identifier.name: f.ttype for f in msg_alias.fields})

    return context.add_alias(msg_alias.new_ttype, new_ty_struct)


def d_policy_instance(context: Context, policy_instance: PolicyInstance) -> Context:
    # The policy name should not already exist
    assert policy_instance.policy_name not in context.typing, errors.POLICY_ALREADY_DEFINED.format(
        policy=policy_instance.policy_name.name
    )
    # TODO: This is not correct, we need to check if the policy is already defined

    policy_struct: TType = context.get_typing(policy_instance.policy_name.name)
    assert isinstance(policy_struct, StructType), errors.POLICY_NOT_STRUCT.format(
        policy=policy_instance.policy_name.name
    )

    # Ensure that all the fields in the policy instance exist in the structure and are well formed
    for parameter in policy_instance.parameters:
        if parameter.identifier.name not in policy_struct.fields:
            context = context.add_error(
                errors.POLICY_FIELD_NOT_FOUND.format(
                    field=parameter.identifier.name,
                    policy_type=policy_instance.policy_name.name,
                    fields=list(policy_struct.fields.keys()),
                )
            )
        else:
            parameter_ttype: RefinedType = selfification(parameter.value, name=parameter.identifier.name)
            # TODO: This is not working correctly, if the value is incorrect, it does not raise an error
            if not is_subtype(context, parameter_ttype, policy_struct.fields[parameter.identifier.name]):
                context = context.add_error(
                    errors.POLICY_FIELD_NOT_SUBTYPE.format(
                        field=parameter.identifier.name,
                        value=parameter.value,
                        ttype=policy_struct.fields[parameter.identifier.name],
                    )
                )

    # Create the new struct type and add it to the context
    new_ty_struct = StructType(
        {
            f.identifier.name: OptionalType(policy_struct.fields[f.identifier.name], f.value)
            for f in policy_instance.parameters
        }
    )

    return context.add_typing(policy_instance.instance_name.name, new_ty_struct)


def d_node_type(context: Context, node_type: NodeType) -> Context:
    context = context.add_typing(node_type.name.name, t_bottom)

    # First, we deal with the configurable parameter, arguments, contextual information
    fields: dict[str, TType] = {}
    for config in node_type.configurable_information:
        config_string, config_ty = st_formation(context, config)
        fields[config_string] = config_ty

        if isinstance(config_ty, OptionalType):
            new_ttype_replaced = inverse_expr_substitution_in_type(
                config_string, config_ty.default_value, config_ty.ttype
            )
            ############################################################################################################
            # PROPERTY: THE DEFAULT VALUE MUST BE A SUBTYPE OF THE TYPE
            if isinstance(config_ty.default_value, Literal) and isinstance(new_ttype_replaced, RefinedType):
                if not interpret(context=context, expr=new_ttype_replaced.refinement):
                    context.add_error(
                        errors.PARAMETER_DEFAULT_INVALID.format(
                            value=config_ty.default_value, parameter=config_string, ttype=config_ty.ttype
                        )
                    )

    connections: list[Union[Publisher, Subscriber, Service, Action, TFTransform]] = []
    for connection in node_type.publishers + node_type.subscribers + node_type.services + node_type.actions:
        connections.append(st_formation(context, connection))

    frames: list[TFTransform] = []
    for frame in node_type.frames:
        frames.append(st_formation(context, frame))

    nodety: TType = NodeT(
        fields=StructType(fields),
        connections=connections,
        frames=frames,
    )

    if node_type.dependency is not None:
        nodety = RefinedType(name=node_type.name, ttype=nodety, refinement=node_type.dependency)

    return context.add_typing(node_type.name.name, nodety)


def d_node_instance(context: Context, node_instance: NodeInstance) -> Context:
    if node_instance.name.name in context.typing:
        return context.add_error(errors.VARIABLE_ALREADY_DEFINED.format(variable=node_instance.name.name))

    context = context.add_typing(node_instance.name.name, t_bottom)
    internal_context = context.add_typing(node_instance.name.name, t_bottom)

    x2_node_type = internal_context.get_typing(node_instance.node_type.name)
    assert isinstance(x2_node_type, NodeT) or isinstance(x2_node_type, RefinedType)

    if isinstance(x2_node_type, RefinedType):
        dependency = x2_node_type.refinement
        x2_node_type = x2_node_type.ttype
        assert isinstance(x2_node_type, NodeT)
    else:
        dependency = None

    # We need to add the types for each variable to the internal_context -- such that we can get their declared type
    for field_name, field_type in x2_node_type.fields.fields.items():
        internal_context = internal_context.add_typing(field_name, field_type)

    # Obtain the values from the node instance
    for config in node_instance.configurable_information:
        st_config_name, st_config_expr = st_formation(internal_context, config)
        if st_config_name not in x2_node_type.fields.fields.keys():
            context = context.add_error(
                errors.CONFIGURABLE_INFORMATION_NOT_FOUND.format(
                    configurable_information=st_config_name,
                    node_instance=node_instance.name.name,
                    node_type=node_instance.node_type.name,
                )
            )
            continue

        internal_context.get_typing(st_config_name)
        interpreted_value = interpret(internal_context, st_config_expr)

        if len(internal_context.temp_default_plugins) > 0:
            # Add all from temp_default_plugins to context.typing
            for plugin_name, plugin_ttype in internal_context.temp_default_plugins.items():
                context = context.add_typing(plugin_name, plugin_ttype)
                if (
                    isinstance(plugin_ttype, PluginT)
                    and plugin_ttype.connections is not None
                    and len(plugin_ttype.connections) > 0
                ):
                    # If the plugin has connections, we need to add them to the context
                    context = context.add_connections(plugin_name, plugin_ttype.connections)
            internal_context.temp_default_plugins = {}

        internal_context = internal_context.add_value(st_config_name, interpreted_value)

    # ##################################################################################################################
    # CHECKING THREE PROPERTIES IN THE SUBTYPING
    node_instance_struct: StructType = StructType(
        {
            field_name: selfification(
                convert_to_expression(context, val, internal_context.get_typing(field_name)), field_name
            )
            for field_name, val in internal_context.values.items()
        }
    )

    if not is_subtype(internal_context, node_instance_struct, x2_node_type.fields):
        for error in internal_context.errors:
            context = context.add_error(error)

    # ##################################################################################################################
    # We need to add the optional values in x2_struct that are not defined in the internal_context
    for y2, t2 in x2_node_type.fields.fields.items():
        if isinstance(t2, OptionalType):
            if y2 in internal_context.values:
                internal_context = internal_context.add_typing(y2, t2.ttype)
            if y2 not in internal_context.values:
                t2_default_interpreted = interpret(internal_context, t2.default_value)

                if len(internal_context.temp_default_plugins) > 0:
                    # Add all from temp_default_plugins to context.typing
                    for plugin_name, plugin_ttype in internal_context.temp_default_plugins.items():
                        context = context.add_typing(plugin_name, plugin_ttype)
                        if (
                            isinstance(plugin_ttype, PluginT)
                            and plugin_ttype.connections is not None
                            and len(plugin_ttype.connections) > 0
                        ):
                            # If the plugin has connections, we need to add them to the context
                            context = context.add_connections(plugin_name, plugin_ttype.connections)
                    internal_context.temp_default_plugins = {}

                internal_context = internal_context.add_value(y2, t2_default_interpreted)

    # ##################################################################################################################
    # PROPERTY: ALL DEPENDENCIES MUST BE SATISFIED
    if dependency is not None:
        if not interpret(internal_context, dependency):
            context = context.add_error(
                errors.DEPENDENCY_NOT_SATISFIED.format(
                    component_instance_type="node",
                    name=node_instance.name.name,
                    dependency=dependency,
                )
            )
    # ##################################################################################################################

    result_connections: list[Union[Publisher, Subscriber, Service, Action, TFTransform]] = copy.deepcopy(
        x2_node_type.connections + x2_node_type.frames
    )

    # Obtain the list of remaps
    remaps: list[tuple[str, str]] = []
    for remap in node_instance.remaps:
        remaps.append(st_formation(internal_context, remap))

    for name, ttype in internal_context.typing.items():
        if isinstance(ttype, PluginT) and name in internal_context.values.values():
            # Add all the connections from the plugin to the node instance
            result_connections.extend(copy.deepcopy(ttype.connections))

    for connection in result_connections:
        for name, value in internal_context.values.items():
            if isinstance(connection, TFTransform):
                substitute_connection_with_assignments(
                    internal_context, connection, name, Literal(value=value, ttype=t_bottom)
                )
            else:
                substitute_connection_with_assignments(
                    internal_context, connection, name, Literal(value=value, ttype=connection.topic.ttype)
                )

        for old_name, new_name in remaps:
            substitute_connection_with_remaps(connection, old_name, new_name)

    return context.add_connections(name=node_instance.name.name, connections=result_connections)


def d_plugin_type(context: Context, plugin_type: PluginType) -> Context:
    context = context.add_typing(plugin_type.name.name, t_bottom)

    # First, we deal with the configurable parameter, arguments, contextual information
    fields: dict[str, TType] = {}
    for config in plugin_type.configurable_information:
        config_string, config_ty = st_formation(context, config)
        fields[config_string] = config_ty

        if isinstance(config_ty, OptionalType):
            new_ttype_replaced = inverse_expr_substitution_in_type(
                config_string, config_ty.default_value, config_ty.ttype
            )
            ############################################################################################################
            # PROPERTY: THE DEFAULT VALUE MUST BE A SUBTYPE OF THE TYPE
            if isinstance(config_ty.default_value, Literal) and isinstance(new_ttype_replaced, RefinedType):
                if not interpret(context=context, expr=new_ttype_replaced.refinement):
                    context.add_error(
                        errors.PARAMETER_DEFAULT_INVALID.format(
                            value=config_ty.default_value, parameter=config_string, ttype=config_ty.ttype
                        )
                    )

    connections: list[Union[Publisher, Subscriber, Service, Action, TFTransform]] = []
    for connection in plugin_type.publishers + plugin_type.subscribers + plugin_type.services + plugin_type.actions:
        connections.append(st_formation(context, connection))

    frames: list[TFTransform] = []
    for frame in plugin_type.frames:
        frames.append(st_formation(context, frame))

    pluginty: TType = PluginT(
        fields=StructType(fields),
        connections=connections,
        frames=frames,
    )

    if plugin_type.dependency is not None:
        pluginty = RefinedType(name=plugin_type.name, ttype=pluginty, refinement=plugin_type.dependency)

    return context.add_typing(plugin_type.name.name, pluginty)


def d_plugin_instance(context: Context, plugin_instance: PluginInstance):
    if plugin_instance.name.name in context.typing:
        return context.add_error(errors.VARIABLE_ALREADY_DEFINED.format(variable=plugin_instance.name.name))

    context = context.add_typing(plugin_instance.name.name, t_bottom)
    internal_context = context.add_typing(plugin_instance.name.name, t_bottom)

    x2_plugin_type = internal_context.get_typing(plugin_instance.plugin_ttype.name)
    assert isinstance(x2_plugin_type, PluginT) or isinstance(x2_plugin_type, RefinedType)

    if isinstance(x2_plugin_type, RefinedType):
        dependency = x2_plugin_type.refinement
        x2_plugin_type = x2_plugin_type.ttype
        assert isinstance(x2_plugin_type, PluginT)
    else:
        dependency = None

    # We need to add the types for each variable to the internal_context -- such that we can get their declared type
    for field_name, field_type in x2_plugin_type.fields.fields.items():
        internal_context = internal_context.add_typing(field_name, field_type)

    # Obtain the values from the node instance
    for config in plugin_instance.configurable_information:
        st_config_name, st_config_expr = st_formation(internal_context, config)
        if st_config_name not in x2_plugin_type.fields.fields.keys():
            context = context.add_error(
                errors.CONFIGURABLE_INFORMATION_NOT_FOUND.format(
                    configurable_information=st_config_name,
                    node_instance=plugin_instance.name.name,
                    node_type=plugin_instance.node_type.name,
                )
            )
            continue

        internal_context.get_typing(st_config_name)
        st_config_expr_interpreted = interpret(internal_context, st_config_expr)

        if len(internal_context.temp_default_plugins) > 0:
            # Add all from temp_default_plugins to context.typing
            for plugin_name, plugin_ttype in internal_context.temp_default_plugins.items():
                context = context.add_typing(plugin_name, plugin_ttype)
                if (
                    isinstance(plugin_ttype, PluginT)
                    and plugin_ttype.connections is not None
                    and len(plugin_ttype.connections) > 0
                ):
                    # If the plugin has connections, we need to add them to the context
                    context = context.add_connections(plugin_name, plugin_ttype.connections)
            internal_context.temp_default_plugins = {}

        internal_context = internal_context.add_value(st_config_name, st_config_expr_interpreted)

    # ##################################################################################################################
    # CHECKING THREE PROPERTIES IN THE SUBTYPING
    plugin_instance_st: StructType = StructType(
        {
            field_name: selfification(
                convert_to_expression(context, val, internal_context.get_typing(field_name)), field_name
            )
            for field_name, val in internal_context.values.items()
        }
    )

    if not is_subtype(internal_context, plugin_instance_st, x2_plugin_type.fields):
        for error in internal_context.errors:
            context = context.add_error(error)

    # ##################################################################################################################
    # We need to add the optional values in x2_struct that are not defined in the internal_context
    for y2, t2 in x2_plugin_type.fields.fields.items():
        if isinstance(t2, OptionalType):
            if y2 in internal_context.values:
                internal_context = internal_context.add_typing(y2, t2.ttype)
            if y2 not in internal_context.values:
                interpreted_y2 = interpret(internal_context, t2.default_value)

                if len(internal_context.temp_default_plugins) > 0:
                    # Add all from temp_default_plugins to context.typing
                    for plugin_name, plugin_ttype in internal_context.temp_default_plugins.items():
                        context = context.add_typing(plugin_name, plugin_ttype)
                        if (
                            isinstance(plugin_ttype, PluginT)
                            and plugin_ttype.connections is not None
                            and len(plugin_ttype.connections) > 0
                        ):
                            # If the plugin has connections, we need to add them to the context
                            context = context.add_connections(plugin_name, plugin_ttype.connections)
                    internal_context.temp_default_plugins = {}

                internal_context = internal_context.add_value(y2, interpreted_y2)

    # ##################################################################################################################
    # PROPERTY: ALL DEPENDENCIES MUST BE SATISFIED
    if dependency is not None:
        if not interpret(internal_context, dependency):
            context = context.add_error(
                errors.DEPENDENCY_NOT_SATISFIED.format(
                    component_instance_type="plugin",
                    name=plugin_instance.name.name,
                    dependency=dependency,
                )
            )
    # ##################################################################################################################

    result_connections: list[Union[Publisher, Subscriber, Service, Action]] = copy.deepcopy(x2_plugin_type.connections)
    result_frames: list[TFTransform] = copy.deepcopy(x2_plugin_type.frames)

    # Obtain the list of remaps
    remaps: list[tuple[str, str]] = []
    for remap in plugin_instance.remaps:
        remaps.append(st_formation(internal_context, remap))

    for connection in result_connections + result_frames:
        for name, value in internal_context.values.items():
            subs_ttype = t_bottom if isinstance(connection, TFTransform) else connection.topic.ttype
            substitute_connection_with_assignments(
                internal_context, connection, name, Literal(value=value, ttype=subs_ttype)
            )

        for old_name, new_name in remaps:
            substitute_connection_with_remaps(connection, old_name, new_name)

    return context.add_typing(
        plugin_instance.name.name,
        PluginT(
            fields=StructType({}),  # There is no reason to keep the fields outside of plugin instance for now
            connections=result_connections,
            frames=result_frames,
        ),
    )


def d_system(context: Context, system: System) -> Context:
    for instances in system.plugin_instances:
        context = def_formation(context, instances)

    for instances in system.node_instances:
        context = def_formation(context, instances)

    system_connections: list[tuple[str, Connection]] = []

    for node, all_connections in context.connections.items():
        system_connections.extend([(node, connection) for connection in all_connections])

    # ##################################################################################################################
    # PROPERTY: ALL CONSUMERS HAVE A PUBLISHER & ALL REFINEMENTS IN CONNECTIONS ARE RESPECTED + QoS PROPERTIES
    for node, connection in system_connections:
        if isinstance(connection, Subscriber):
            if isinstance(connection.topic.ttype, RefinedType):
                if not interpret(context, connection.topic.ttype.refinement):
                    context = context.add_error(
                        errors.CONNECTION_REFINEMENT_NOT_SATISFIED.format(
                            refinement=connection.topic.ttype.refinement, connection=connection
                        )
                    )
            else:
                pub_connections = interpret_connection(context, connection.topic, Publisher)

                if len(pub_connections) == 0:
                    context = context.add_error(
                        errors.PUBLISHER_NOT_FOUND.format(topic=connection.topic, component=node)
                    )

                for conn2 in pub_connections:
                    if not is_subtype(context, conn2.topic.ttype, connection.topic.ttype):
                        context = context.add_error(
                            errors.CONNECTION_NOT_SUBTYPE.format(
                                connection=connection, expected_type=connection.topic.ttype, component=node
                            )
                        )

                    # ##################################################################################################
                    # PROPERTY: CHECK IF THE QOS MATCH BETWEEN THE SUBSCRIBER AND THE PUBLISHER
                    check_policies(context, connection.policies, conn2.policies)

        if isinstance(connection, Publisher):
            if isinstance(connection.topic.ttype, RefinedType):
                if not interpret(context, connection.topic.ttype.refinement):
                    context = context.add_error(
                        errors.CONNECTION_REFINEMENT_NOT_SATISFIED.format(
                            refinement=connection.topic.ttype.refinement, connection=connection
                        )
                    )

                # TODO: QoS consistency, if there is another publisher with the same topic and qos, check compatibility

        if isinstance(connection, Service):
            if isinstance(connection.topic.ttype, RefinedType):
                if not interpret(context, connection.topic.ttype.refinement):
                    context = context.add_error(
                        errors.CONNECTION_REFINEMENT_NOT_SATISFIED.format(
                            refinement=connection.topic.ttype.refinement, connection=connection
                        )
                    )
            else:
                provider_connections = interpret_connection(context, connection.topic, Service)
                provider_connections = [x for x in provider_connections if x.role == ServiceActionRole.PROVIDES]

                if len(provider_connections) == 0:
                    context = context.add_error(errors.PROVIDER_NOT_FOUND.format(connection=connection, component=node))

                for conn2 in provider_connections:
                    if not is_subtype(context, conn2.topic.ttype, connection.topic.ttype):
                        context = context.add_error(
                            errors.CONNECTION_NOT_SUBTYPE.format(
                                connection=connection, expected_type=connection.topic.ttype, component=node
                            )
                        )

                    # ##################################################################################################
                    # PROPERTY: CHECK IF THE QOS MATCH BETWEEN THE CONSUMER AND PROVIDER
                    check_policies(context, connection.policies, conn2.policies)

        if isinstance(connection, Action):
            if isinstance(connection.topic.ttype, RefinedType):
                if not interpret(context, connection.topic.ttype.refinement):
                    context = context.add_error(
                        errors.CONNECTION_REFINEMENT_NOT_SATISFIED.format(
                            refinement=connection.topic.ttype.refinement, connection=connection
                        )
                    )
            else:
                provider_connections = interpret_connection(context, connection.topic, Action)
                provider_connections = [x for x in provider_connections if x.role == ServiceActionRole.PROVIDES]
                number_of_providers = len(provider_connections)
                if number_of_providers == 0:
                    context = context.add_error(
                        errors.PROVIDER_NOT_FOUND.format(topic=connection.topic, component=node)
                    )

                for conn2 in provider_connections:
                    if not is_subtype(context, conn2.topic.ttype, connection.topic.ttype):
                        context = context.add_error(
                            errors.CONNECTION_NOT_SUBTYPE.format(
                                connection=connection, expected_type=connection.topic.ttype, component=node
                            )
                        )

                    # ##################################################################################################
                    # PROPERTY: CHECK IF THE QOS MATCH BETWEEN THE CONSUMER AND PROVIDER
                    check_policies(context, connection.policies, conn2.policies)

    # ##################################################################################################################
    # PROPERTY: BROADCAST + LISTENS CONNECTIONS ARE WELL FORMED
    for index, (node, connection) in enumerate(system_connections):
        if isinstance(connection, TFTransform):
            if connection.transform == TransformType.LISTEN:
                listener_child = interpret(context, connection.child_frame)
                listener_parent = interpret(context, connection.parent_frame)

                broadcasters = []
                for conn2 in system_connections[index + 1 :]:
                    if isinstance(conn2, TFTransform) and conn2.transform == TransformType.BROADCAST:
                        broadcaster_child = interpret(context, conn2.child_frame)
                        broadcaster_parent = interpret(context, conn2.parent_frame)
                        if listener_child == broadcaster_child and listener_parent == broadcaster_parent:
                            broadcasters.append(conn2)
                if len(broadcasters) == 0:
                    context = context.add_error(
                        errors.BROADCASTER_NOT_FOUND.format(listener=connection, component=node)
                    )

            if connection.transform == TransformType.BROADCAST:
                broadcast1_child = interpret(context, connection.child_frame)
                broadcast1_parent = interpret(context, connection.parent_frame)
                other_broadcasters = []
                for node2, conn2 in system_connections[index + 1 :]:
                    if isinstance(conn2, TFTransform) and conn2.transform == TransformType.BROADCAST:
                        broadcast2_child = interpret(context, conn2.child_frame)
                        broadcast2_parent = interpret(context, conn2.parent_frame)
                        if broadcast1_child == broadcast2_child:
                            other_broadcasters.append(conn2)

                        # TODO: we need proper algorithm to find cycles in graph
                        if broadcast1_parent == broadcast2_child and broadcast1_child == broadcast2_parent:
                            context = context.add_error(
                                errors.BROADCASTER_CYCLIC.format(
                                    child_frame=connection.child_frame,
                                    parent_frame=connection.parent_frame,
                                )
                            )

                if len(other_broadcasters) > 0:
                    context = context.add_error(
                        errors.BROADCASTER_MULTIPLE_PARENTS.format(
                            child_frame=connection.child_frame,
                            parent_frame=connection.parent_frame,
                            parents=[broadcaster.node.name for broadcaster in other_broadcasters] + [node],
                        )
                    )

    return context


def program_formation(context: Context, program: Program) -> list[str]:
    for policy_instance in program.policy_instances:
        context = def_formation(context, policy_instance)
    for type_alias in program.type_aliases:
        context = def_formation(context, type_alias)
    for msg_alias in program.message_aliases:
        context = def_formation(context, msg_alias)
    for node_type in program.node_types:
        context = def_formation(context, node_type)
    for plugin_type in program.plugin_types:
        context = def_formation(context, plugin_type)

    # Finally check the systems
    for system in program.system:
        context = def_formation(context, system)

    return context.errors


def def_formation(context: Context, definition: ROSpecNode) -> Context:
    dispatcher = {
        TypeAlias: d_type_alias,
        MessageAlias: d_message_alias,
        PolicyInstance: d_policy_instance,
        NodeType: d_node_type,
        NodeInstance: d_node_instance,
        PluginType: d_plugin_type,
        PluginInstance: d_plugin_instance,
        System: d_system,
    }
    return dispatcher[type(definition)](context, definition)
