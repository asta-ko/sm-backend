from collections import OrderedDict

from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication


class BTokenAuthentication(ExpiringTokenAuthentication):
    keyword = 'bearer'  # needed for frontend


class SkipNullValuesMixin(object):
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # KEY IS HERE:
            if attribute in [None, '']:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


def save_dict_or_pk_return_dict(serializer_class, string_field='title', required=False, max_length=None, **kwargs):
    """
    Accept strings and pks. If got string, get or create model instance based on string_field
    Representation - return an object (depending on model_class).
    """

    class PrimaryKeyNestedMixin(serializer_class):

        def to_internal_value(self, data):

            if not data and not required:
                return ""

            user = self.context['request'].user
            if isinstance(data, str):
                if max_length and len(data > max_length):
                    self.fail('string too long')
                try:
                    strdata = {'user': user}
                    strdata[string_field] = data
                    instance, created = serializer_class.Meta.model.objects.get_or_create(**strdata)
                    return instance
                except (TypeError, ValueError):
                    self.fail('incorrect_type', data_type=type(data).__name__)

            if isinstance(data, int):
                try:
                    instance = serializer_class.Meta.model.objects.get(pk=data)
                    return instance
                except serializer_class.Meta.model.DoesNotExist:
                    self.fail('does_not_exist', pk_value=data)
                except (TypeError, ValueError):
                    self.fail('incorrect_type', data_type=type(data).__name__)

            obj_data = serializer_class.to_internal_value(self, data)
            obj_data['user'] = user
            instance, created = serializer_class.Meta.model.objects.get_or_create(**obj_data)
            return instance

        def to_representation(self, data):
            return serializer_class.to_representation(self, data)

    return PrimaryKeyNestedMixin(**kwargs)
