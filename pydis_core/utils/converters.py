from datetime import UTC, datetime

import dateutil.parser
from discord.ext.commands import BadArgument, Context, Converter


class ISODateTime(Converter):
    """Converts an ISO-8601 datetime string into a datetime.datetime."""

    async def convert(self, _context: Context, datetime_string: str) -> datetime:
        """
        Converts an ISO-8601 ``datetime_string`` into a ``datetime.datetime`` object.

        The converter is flexible in the formats it accepts, as it uses the :meth:`isoparse <dateutil.parser.isoparse>`
        method of :mod:`dateutil.parser`. In general, it accepts datetime strings that start with a date,
        optionally followed by a time. Specifying a timezone offset in the datetime string is
        supported, but the ``datetime`` object will be converted to UTC. If no timezone is specified, the datetime will
        be assumed to be in UTC already. In all cases, the returned object will have the UTC timezone.

        See: https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.isoparse

        Formats that are guaranteed to be valid by our tests are:

        - ``YYYY-mm-ddTHH:MM:SSZ`` | ``YYYY-mm-dd HH:MM:SSZ``
        - ``YYYY-mm-ddTHH:MM:SS±HH:MM`` | ``YYYY-mm-dd HH:MM:SS±HH:MM``
        - ``YYYY-mm-ddTHH:MM:SS±HHMM`` | ``YYYY-mm-dd HH:MM:SS±HHMM``
        - ``YYYY-mm-ddTHH:MM:SS±HH`` | ``YYYY-mm-dd HH:MM:SS±HH``
        - ``YYYY-mm-ddTHH:MM:SS`` | ``YYYY-mm-dd HH:MM:SS``
        - ``YYYY-mm-ddTHH:MM`` | ``YYYY-mm-dd HH:MM``
        - ``YYYY-mm-dd``
        - ``YYYY-mm``
        - ``YYYY``

        .. note::

           ISO-8601 specifies a ``T`` as the separator between the date and the time part of the
           datetime string. The converter accepts both a ``T`` and a single space character.

        :rtype: datetime.datetime
        """
        try:
            dt = dateutil.parser.isoparse(datetime_string)
        except ValueError:
            raise BadArgument(f"`{datetime_string}` is not a valid ISO-8601 datetime string")

        if dt.tzinfo:
            dt = dt.astimezone(UTC)
        else:  # Without a timezone, assume it represents UTC.
            dt = dt.replace(tzinfo=UTC)

        return dt
